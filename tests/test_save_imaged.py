# Copyright 2020 - 2021 MONAI Consortium
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import tempfile
import unittest

import numpy as np
import torch
from parameterized import parameterized

from monai.transforms import SaveImaged

TEST_CASE_0 = [
    {
        "img": torch.randint(0, 255, (8, 1, 2, 3, 4)),
        "img_meta_dict": {"filename_or_obj": ["testfile" + str(i) + ".nii.gz" for i in range(8)]},
    },
    ".nii.gz",
    False,
    True,
]

TEST_CASE_1 = [
    {
        "img": torch.randint(0, 255, (8, 1, 2, 3), dtype=torch.uint8),
        "img_meta_dict": {"filename_or_obj": ["testfile" + str(i) + ".png" for i in range(8)]},
    },
    ".png",
    False,
    True,
]

TEST_CASE_2 = [
    {
        "img": np.random.randint(0, 255, (8, 1, 2, 3, 4)),
        "img_meta_dict": {"filename_or_obj": ["testfile" + str(i) + ".nii.gz" for i in range(8)]},
    },
    ".nii.gz",
    False,
    True,
]

TEST_CASE_3 = [
    {
        "img": torch.randint(0, 255, (8, 1, 2, 2)),
        "img_meta_dict": {
            "filename_or_obj": ["testfile" + str(i) + ".nii.gz" for i in range(8)],
            "spatial_shape": [(28, 28)] * 8,
            "affine": [np.diag(np.ones(4)) * 5] * 8,
            "original_affine": [np.diag(np.ones(4)) * 1.0] * 8,
        },
    },
    ".nii.gz",
    True,
    True,
]

TEST_CASE_4 = [
    {
        "img": torch.randint(0, 255, (8, 1, 2, 3), dtype=torch.uint8),
        "img_meta_dict": {
            "filename_or_obj": ["testfile" + str(i) + ".png" for i in range(8)],
            "spatial_shape": [(28, 28)] * 8,
        },
    },
    ".png",
    True,
    True,
]

TEST_CASE_5 = [
    {
        "img": torch.randint(0, 255, (1, 2, 3, 4)),
        "img_meta_dict": {"filename_or_obj": "testfile0.nii.gz"},
    },
    ".nii.gz",
    False,
    False,
]

TEST_CASE_6 = [
    {
        "img": torch.randint(0, 255, (1, 2, 3, 4)),
        "img_meta_dict": {"filename_or_obj": "testfile0.nii.gz"},
        "patch_index": 6,
    },
    ".nii.gz",
    False,
    False,
]

TEST_CASE_7 = [
    {
        "pred": torch.randint(0, 255, (8, 1, 2, 2)),
        "img_meta_dict": {
            "filename_or_obj": ["testfile" + str(i) + ".nii.gz" for i in range(8)],
            "spatial_shape": [(28, 28)] * 8,
            "affine": [np.diag(np.ones(4)) * 5] * 8,
            "original_affine": [np.diag(np.ones(4)) * 1.0] * 8,
        },
    },
    ".nii.gz",
    True,
    True,
]


class TestSaveImaged(unittest.TestCase):
    @parameterized.expand([TEST_CASE_0, TEST_CASE_1, TEST_CASE_2, TEST_CASE_3, TEST_CASE_4, TEST_CASE_5, TEST_CASE_6])
    def test_saved_content(self, test_data, output_ext, resample, save_batch):
        with tempfile.TemporaryDirectory() as tempdir:
            trans = SaveImaged(
                keys=["img", "pred"],
                meta_keys="img_meta_dict",
                output_dir=tempdir,
                output_ext=output_ext,
                resample=resample,
                save_batch=save_batch,
                allow_missing_keys=True,
            )
            trans(test_data)

            if save_batch:
                for i in range(8):
                    filepath = os.path.join("testfile" + str(i), "testfile" + str(i) + "_trans" + output_ext)
                    self.assertTrue(os.path.exists(os.path.join(tempdir, filepath)))
            else:
                patch_index = test_data["img_meta_dict"].get("patch_index", None)
                patch_index = f"_{patch_index}" if patch_index is not None else ""
                filepath = os.path.join("testfile0", "testfile0" + "_trans" + patch_index + output_ext)
                self.assertTrue(os.path.exists(os.path.join(tempdir, filepath)))


if __name__ == "__main__":
    unittest.main()
