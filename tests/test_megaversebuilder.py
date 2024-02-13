from asyncio import timeout
import unittest
from unittest.mock import patch, MagicMock
from crossmint_megaverse.MegaverseBuilder import MegaverseBuilder

class TestMegaverseBuilder(unittest.TestCase):
    def setUp(self):
        self.candidate_id = "test_candidate_id"
        self.builder = MegaverseBuilder(self.candidate_id)

    @patch("requests.get")
    def test_get_goal_map_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"goal": [["POLYANET", "SPACE", "POLYANET"],
                                                            ["SPACE", "POLYANET", "SPACE"],
                                                            ["POLYANET", "SPACE", "POLYANET"]]}
        self.assertTrue(self.builder.get_goal_map())
        self.assertEqual(self.builder.goal_map, [["POLYANET", "SPACE", "POLYANET"],
                                                 ["SPACE", "POLYANET", "SPACE"],
                                                 ["POLYANET", "SPACE", "POLYANET"]])
        
    @patch("requests.get")
    def test_get_goal_map_failure(self, mock_get):
        mock_get.return_value.status_code = 404
        self.assertFalse(self.builder.get_goal_map())
        self.assertIsNone(self.builder.goal_map)

    def test_parse_goal_map_valid(self):
        goal_map = [["SPACE", "SPACE", "SPACE"],
                    ["SPACE", "POLYANET", "SPACE"],
                    ["SPACE", "SPACE", "SPACE"]]
        celestial_bodies = self.builder.parse_goal_map(goal_map)
        expected_celestial_bodies = [("POLYANET", 1, 1)]
        self.assertEqual(celestial_bodies, expected_celestial_bodies)

    def test_parse_goal_map_invalid(self):
        goal_map = [["SPACE", "SPACE", "SPACE"],
                    ["SPACE", "POLYANET", "SPACE"],
                    "SPACE"]
        celestial_bodies = self.builder.parse_goal_map(goal_map)
        self.assertEqual(celestial_bodies, [])

    @patch("requests.post")
    def test_place_celestial_bodies_success(self, mock_post):
        celestial_bodies = [("POLYANET", 1, 1)]
        mock_post.return_value.status_code = 200
        self.builder.place_celestial_bodies(celestial_bodies)
        self.assertEqual(mock_post.call_count, 1)

    @patch("requests.post")
    def test_place_celestial_bodies_rate_limit(self, mock_post):
        celestial_bodies = [("POLYANET", 1, 1)]
        mock_post.side_effect = [
            MagicMock(status_code=429),
            MagicMock(status_code=200)
        ]
        self.builder.place_celestial_bodies(celestial_bodies)
        expected_calls = [
            unittest.mock.call(
                "https://challenge.crossmint.io/api/polyanets",
                json={"row": 1, "column": 1, "candidateId": self.candidate_id}
            ),
            unittest.mock.call(
                "https://challenge.crossmint.io/api/polyanets",
                json={"row": 1, "column": 1, "candidateId": self.candidate_id}
            )
        ]
        mock_post.assert_has_calls(expected_calls)

    @patch("requests.post")
    def test_place_celestial_bodies_failure(self, mock_post):
        celestial_bodies = [("POLYANET", 1, 1)]
        mock_post.return_value.status_code = 500
        self.builder.place_celestial_bodies(celestial_bodies)
        self.assertEqual(mock_post.call_count, 1)

if __name__ == "__main__":
    unittest.main()