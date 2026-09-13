import hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('verifier',ROOT/'verify_package.py');verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier)
class PackageIntegrity(unittest.TestCase):
    def test_exact_inventory_and_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'workflows').mkdir()
            source=next((ROOT/'workflows').glob('*.json'))
            (root/'workflows'/source.name).write_bytes(source.read_bytes())
            model=root/'models.json';original=(ROOT/'models.json').read_bytes();model.write_bytes(original)
            hashes={f.relative_to(root).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in root.rglob('*') if f.is_file()}
            (root/'SHA256SUMS.json').write_text(json.dumps(hashes));verifier.verify(root)
            model.write_text('{}')
            with self.assertRaisesRegex(ValueError,'SHA256 mismatch'):verifier.verify(root)
            model.unlink()
            with self.assertRaisesRegex(ValueError,'Missing:'):verifier.verify(root)
            model.write_bytes(original);extra=root/'unexpected.txt';extra.write_text('x')
            with self.assertRaisesRegex(ValueError,'Extra:'):verifier.verify(root)
            extra.unlink();verifier.verify(root)
if __name__=='__main__':unittest.main()
