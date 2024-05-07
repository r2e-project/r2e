import unittest

from r2e.models import Repo
from r2e.repo_builder.fut_extractor.extract_repo_data import extract_repo_data


class TestExtractRepoData(unittest.TestCase):
    def test_1(self):
        repo_dict = {
            "repo_org": "",
            "repo_name": "klongpy",
            "repo_id": "klongpy",
            "local_repo_path": "repos/klongpy",
            "_cached_callgraph": None,
        }
        repo = Repo(**repo_dict)

        extract_repo_data(repo)
