"""Regression tests for destructive-cleaning, annotation and leakage failures."""
import csv
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image
import yaml
from data_tools.dataset_audit import audit_yaml, check_label_file, sha256
from data_tools.prepare_data_fixed import prepare_data
from data_tools.split_manifest_fixed import create_manifest

class DatasetTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        for s in ("train","val","test"):
            (self.root/"images"/s).mkdir(parents=True)
            (self.root/"labels"/s).mkdir(parents=True)
            Image.new("RGB",(32,32),{"train":"red","val":"green","test":"blue"}[s]).save(self.root/"images"/s/"one.png")
            (self.root/"labels"/s/"one.txt").write_text("0 0.5 0.5 0.5 0.5\n",encoding="utf8")
        self.yaml=self.root/"data.yaml"
        self.yaml.write_text(yaml.safe_dump({"path":".","train":"images/train","val":"images/val","test":"images/test","names":["defect"]}),encoding="utf8")
    def tearDown(self): self.temp.cleanup()
    def test_legacy_single_split_api(self):
        from data_tools.check_label_fixed import check_dataset
        result=check_dataset(self.root/"images/train",self.root/"labels/train",1)
        self.assertTrue(result["passed"])
    def test_clean_dataset(self):
        r=audit_yaml(self.yaml,require_test=True)
        self.assertTrue(r["passed"])
        self.assertEqual(r["group_status"],"not_verified")
    def test_empty_labels_are_preserved(self):
        label=self.root/"labels/train/one.txt";label.write_text("",encoding="utf8")
        before={str(p):sha256(p) for p in self.root.rglob("*") if p.is_file()}
        r=prepare_data(self.root/"images/train",self.root/"labels/train",1)
        self.assertEqual(r["items"][0]["status"],"valid_negative")
        self.assertEqual(before,{str(p):sha256(p) for p in self.root.rglob("*") if p.is_file()})
    def test_missing_labels_are_preserved(self):
        (self.root/"labels/train/one.txt").unlink()
        r=prepare_data(self.root/"images/train",self.root/"labels/train",1)
        self.assertIn("missing_label",r["items"][0]["errors"])
        self.assertTrue((self.root/"images/train/one.png").exists())
    def test_invalid_numeric_and_class_values(self):
        cases=["0 0.5 0.5 0.2","1 0.5 0.5 0.2 0.2","0.5 0.5 0.5 0.2 0.2",
               "-1 0.5 0.5 0.2 0.2","0 nan 0.5 0.2 0.2","0 inf 0.5 0.2 0.2",
               "0 0.5 0.5 0 0.2","0 0.1 0.5 0.5 0.2","0 1.1 0.5 0.2 0.2",
               "0 foo 0.5 0.2 0.2","0 0.5 0.5 0.2 0.2\n0 0.5 0.5 0.2 0.2"]
        p=self.root/"labels/train/one.txt"
        for text in cases:
            with self.subTest(text=text):
                p.write_text(text,encoding="utf8")
                self.assertTrue(check_label_file(p,1)[1])
    def test_valid_edge_and_whitespace(self):
        p=self.root/"labels/train/one.txt";p.write_text("\n0 0.5 0.5 1 1\n\n",encoding="utf8")
        self.assertFalse(check_label_file(p,1)[1])
    def test_duplicate_leakage(self):
        (self.root/"images/val/one.png").write_bytes((self.root/"images/train/one.png").read_bytes())
        r=audit_yaml(self.yaml)
        self.assertFalse(r["passed"])
        self.assertTrue(any(d["cross_split"] for d in r["duplicates"]))
    def test_damaged_image(self):
        (self.root/"images/test/one.png").write_bytes(b"not an image")
        r=audit_yaml(self.yaml,require_test=True)
        self.assertTrue(any("bad_image" in e["error"] for e in r["errors"]))
    def test_group_leakage_and_missing_mapping(self):
        p=self.root/"groups.csv"
        p.write_text("image,group_id\nimages/train/one.png,part1\nimages/val/one.png,part1\n",encoding="utf8")
        r=audit_yaml(self.yaml,p)
        self.assertTrue(any(e["error"]=="related_group_crosses_splits" for e in r["errors"]))
        self.assertTrue(any(e["error"]=="missing_group_id" for e in r["errors"]))
    def test_manifest_is_deterministic_and_no_overwrite(self):
        p=self.root/"manifest.txt";a=create_manifest(self.root/"images/train",p)
        q=self.root/"other.txt";b=create_manifest(self.root/"images/train",q)
        self.assertEqual(a,b)
        with self.assertRaises(FileExistsError):create_manifest(self.root/"images/train",p)
    def test_yaml_manifest_paths(self):
        p=self.root/"list.txt"
        p.write_text("./images/train/one.png\n",encoding="utf8")
        data=yaml.safe_load(self.yaml.read_text());data["train"]="list.txt"
        self.yaml.write_text(yaml.safe_dump(data),encoding="utf8")
        self.assertTrue(audit_yaml(self.yaml)["passed"])
    def test_missing_test(self):
        data=yaml.safe_load(self.yaml.read_text());del data["test"]
        self.yaml.write_text(yaml.safe_dump(data),encoding="utf8")
        self.assertTrue(audit_yaml(self.yaml)["passed"])
        self.assertFalse(audit_yaml(self.yaml,require_test=True)["passed"])
    def test_shared_label_stems_rejected(self):
        Image.new("RGB",(32,32),"purple").save(self.root/"images/train/one.jpg")
        self.assertFalse(audit_yaml(self.yaml)["passed"])

if __name__=="__main__":
    unittest.main(verbosity=2)
