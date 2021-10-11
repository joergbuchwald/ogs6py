import shutil
import unittest
from context import ogs6py
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
        with self.assertRaises(RuntimeError) as cm:
            model.run_model(path="not/a/dir", container_path=sif_file.name)
        self.assertEqual('The specified path is not a directory. Please provide a directory containing the Singularity executable.',
            str(cm.exception))
        # case: container_path is not a file:
        with self.assertRaises(RuntimeError) as cm:
            model.run_model(container_path="not/a/file")
        self.assertEqual('The specific container-path is not a file. Please provide a path to the OGS container.',
            str(cm.exception))
        # case: container_path is not a *.sif file
        with self.assertRaises(RuntimeError) as cm:
            model.run_model(container_path=x_file.name)
        self.assertEqual('The specific file is not a Singularity container. Please provide a *.sif file containing OGS.',
            str(cm.exception))
        # case Singularity executable not found without path
        if shutil.which(os.path.join("singularity")) is None:
            with self.assertRaises(RuntimeError) as cm:
                model.run_model(container_path=sif_file.name)
            self.assertEqual('The Singularity executable was not found. See https://www.opengeosys.org/docs/userguide/basics/container/ for installation instructions.',
                str(cm.exception))
        # case Singularity executable not found in path
        with self.assertRaises(RuntimeError) as cm:
            model.run_model(path=sing_dir.name, container_path=sif_file.name)
        self.assertEqual('The Singularity executable was not found. See https://www.opengeosys.org/docs/userguide/basics/container/ for installation instructions.',
            str(cm.exception))
        
        # clean up the temporary dir
        sing_dir.cleanup()
        
if __name__ == '__main__':
    unittest.main()