import unittest
from crossmint_megaverse.MegaverseBuilder import MegaverseBuilder
from unittest.mock import patch

class TestMegaverseBuilder(unittest.TestCase):
    def setUp(self):
        self.candidate_id = "test_candidate_id"
        self.builder = MegaverseBuilder(self.candidate_id)

    @patch("requests.get")
    def test_get_goal_map_success(self, mock_get):
        goal_map = [["POLYANET", "SPACE", "POLYANET"],
                    ["SPACE", "POLYANET", "SPACE"],
                    ["POLYANET", "SPACE", "POLYANET"]]
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"goal": goal_map}
        self.assertTrue(self.builder.get_goal_map())
        self.assertEqual(self.builder.goal_map, goal_map)

    @patch("requests.get")
    def test_get_goal_map_failure(self, mock_get):
        mock_get.return_value.status_code = 404
        with patch.object(self.builder.logger, 'error') as mock_logger_error:
            self.assertFalse(self.builder.get_goal_map())
            mock_logger_error.assert_called_once_with("Failed to retrieve default map: %d", 404)

    def test_parse_goal_map_valid_simple(self):
        goal_map = [["SPACE", "SPACE", "SPACE"],
                    ["SPACE", "POLYANET", "SPACE"],
                    ["SPACE", "SPACE", "SPACE"]]
        celestial_bodies = self.builder.parse_goal_map(goal_map)
        expected_celestial_bodies = [("POLYANET", 1, 1)]
        self.assertEqual(celestial_bodies, expected_celestial_bodies)
    
    def test_parse_goal_map_valid_complex(self):
        goal_map = [["SPACE", "SPACE", "SPACE"],
                    ["SPACE", "UP_COMETH", "SPACE", "DOWN_COMETH"],
                    ["SPACE", "SPACE", "UP_COMETH", "DOWN_COMETH"]]
        
        celestial_bodies = self.builder.parse_goal_map(goal_map)
        expected_celestial_bodies = [("UP_COMETH", 1, 1), ("DOWN_COMETH", 1, 3), ("UP_COMETH", 2, 2), ("DOWN_COMETH", 2, 3)]
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
        mock_post.assert_called_once_with(
            "https://challenge.crossmint.io/api/polyanets",
            json={"row": 1, "column": 1, "candidateId": self.candidate_id}
        )

    @patch("requests.post")
    def test_place_celestial_bodies_failure(self, mock_post):
        celestial_bodies = [("POLYANET", 1, 1)]
        mock_post.return_value.status_code = 500
        self.builder.place_celestial_bodies(celestial_bodies)
        self.assertEqual(mock_post.call_count, 1)

    def test_place_celestial_bodies_multiple_calls(self):
        celestial_bodies = [("POLYANET", 1, 1), ("UP_COMETH", 2, 2), ("DOWN_COMETH", 2, 3)]
        with patch("requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            self.builder.place_celestial_bodies(celestial_bodies)
            self.assertEqual(mock_post.call_count, 3)
    
    @patch("requests.post")
    def test_place_celestial_bodies_invalid_color(self, mock_post):
        celestial_bodies = [("SOLOON_INVALID", 1, 1)]
        self.builder.place_celestial_bodies(celestial_bodies)
        self.assertEqual(mock_post.call_count, 0)

    @patch("requests.post")
    def test_place_celestial_bodies_invalid_direction(self, mock_post):
        celestial_bodies = [("COMETH_INVALID", 1, 1)]
        self.builder.place_celestial_bodies(celestial_bodies)
        self.assertEqual(mock_post.call_count, 0)

    @patch("requests.post")
    def test_place_celestial_bodies_unknown_type(self, mock_post):
        celestial_bodies = [("UNKNOWN_BODY_TYPE", 1, 1)]
        self.builder.place_celestial_bodies(celestial_bodies)
        self.assertEqual(mock_post.call_count, 0)

if __name__ == "__main__":
    unittest.main()