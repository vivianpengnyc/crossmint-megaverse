import requests
import time
import logging
from typing import List, Tuple


class MegaverseBuilder:
    def __init__(self, candidate_id: str) -> None:
        self.candidate_id = candidate_id
        self.goal_map = None
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def get_goal_map(self) -> bool:
        url = f"https://challenge.crossmint.io/api/map/{self.candidate_id}/goal"
        response = requests.get(url)
        if response.status_code == 200:
            map_data = response.json().get("goal")
            self.goal_map = map_data
            return True
        else:
            self.logger.error("Failed to retrieve default map: %d", response.status_code)
            return False

    def parse_goal_map(self, goal_map: List[List[str]]) -> List[Tuple[str, int, int]]:
        if not isinstance(goal_map, list) or not all(isinstance(row, list) for row in goal_map):
            self.logger.error("Invalid goal map format. Expecting a list of lists.")
            return []

        celestial_bodies = []
        for row_index, row in enumerate(goal_map):
            for column_index, cell in enumerate(row):
                if cell != "SPACE":
                    celestial_bodies.append((cell, row_index, column_index))
        return celestial_bodies

    def place_celestial_bodies(self, celestial_bodies: List[Tuple[str, int, int]]) -> None:
        for body_type, row, col in celestial_bodies:
            retry_delay = 1  # Initial retry delay
            max_retries = 3  # Maximum number of retries
            retry_count = 0
            while retry_count < max_retries:
                try:
                    if body_type == "POLYANET":
                        endpoint = "polyanets"
                        data = {"row": row, "column": col, "candidateId": self.candidate_id}

                    elif "SOLOON" in body_type:
                        endpoint = "soloons"
                        color = body_type.split('_')[0]
                        if not self.check_soloon_color(color):
                            self.logger.error("Invalid color for SOLOON: %s", color)
                            break
                        data = {"row": row, "column": col, "color": color.lower(), "candidateId": self.candidate_id}

                    elif "COMETH" in body_type:
                        endpoint = "comeths"
                        direction = body_type.split('_')[0]
                        if not self.check_cometh_direction(direction):
                            self.logger.error("Invalid direction for COMETH: %s", direction)
                            break
                        data = {"row": row, "column": col, "direction": direction.lower(), "candidateId": self.candidate_id}

                    else:
                        self.logger.error("Unknown celestial body type: %s", body_type)
                        break

                    response = requests.post(f"https://challenge.crossmint.io/api/{endpoint}", json=data)
                    response.raise_for_status()
                    self.logger.info(f"Placed {body_type} at row {row}, column {col}. Response: {response.status_code}")
                    break  # Successful placement
                except requests.exceptions.RequestException as e:
                    if retry_count == max_retries - 1:
                        self.logger.error(f"Failed to place {body_type} at row {row}, column {col}. Response: {str(e)}")
                    else:
                        self.logger.warning("Too many requests. Waiting for cooldown...")
                        time.sleep(retry_delay)  # Wait before retrying
                        retry_delay *= 2  # Exponential backoff
                        retry_count += 1
    
    def check_soloon_color(self, color: str) -> bool:
        valid_colors = {"blue", "red", "purple", "white"}
        return color.lower() in valid_colors

    def check_cometh_direction(self, direction: str) -> bool:
        valid_directions = {"up", "down", "left", "right"}
        return direction.lower() in valid_directions

def main():
    candidate_id = "d0cd286e-7ab6-40e6-84a3-b8e7805a86df"
    builder = MegaverseBuilder(candidate_id)

    # Task 1
    if builder.get_goal_map():
        celestial_bodies = builder.parse_goal_map(builder.map)
        builder.place_celestial_bodies(celestial_bodies)
    else:
        print("Failed to retrieve default map")

    # Task 2
    if builder.get_goal_map():
        celestial_bodies = builder.parse_goal_map(builder.map)
        builder.place_celestial_bodies(celestial_bodies)
    else:
        print("Failed to retrieve default map")

if __name__ == "__main__":
    main()





