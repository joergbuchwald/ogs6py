import shutil
import unittest
import ogs6py
import tempfile
import os

class TestiOGSModelrun(unittest.TestCase):

    def test_model_run(self):
        prjfile = "tests/tunnel_ogs6py.prj"
        # dummy *.SIF file
        sif_file = tempfile.NamedTemporaryFile(suffix=".sif")
        # dummy *.notSIF file
        x_file = tempfile.NamedTemporaryFile(suffix=".x")
        # dummy directory
        sing_dir = tempfile.TemporaryDirectory()
        
        # case: path is not a dir
        model = ogs6py.OGS(INPUT_FILE=prjfile, PROJECT_FILE=prjfile)
        with self.assertRaises(RuntimeError):
            model.run_model(container=True, path="not/a/dir")
        # case: container_path is not a file:
        with self.assertRaises(RuntimeError):
            model.run_model(container=True, container_path="not/a/file")
        # case: container_path is not a *.sif file
        with self.assertRaises(RuntimeError):
            model.run_model(container=True, container_path=x_file.name)
        # case: container_path is missing
        with self.assertRaises(RuntimeError):
            model.run_model(container=True)
        # case Singularity executable not found without path
        if shutil.which(os.path.join("singularity")) is None:
            with self.assertRaises(RuntimeError):
                model.run_model(container=True, container_path=sif_file.name)
        # case Singularity executable not found in path
        with self.assertRaises(RuntimeError):
            model.run_model(container=True, path=sing_dir.name, container_path=sif_file.name)
        
        # clean up the temporary dir
        sing_dir.cleanup()
        
if __name__ == '__main__':
    unittest.main()