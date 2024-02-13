import requests
import time
import logging

class MegaverseBuilder:
    def __init__(self, candidate_id) -> None:
        self.candidate_id = candidate_id
        self.goal_map = None
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def get_goal_map(self):
        url = f"https://challenge.crossmint.io/api/map/{self.candidate_id}/goal"
        response = requests.get(url)
        if response.status_code == 200:
            map_data = response.json().get("goal")
            self.goal_map = map_data
            return True
        else:
            self.logger.error("Failed to retrieve default map: %d", response.status_code)
            return False
    
    def parse_goal_map(self, goal_map):
        if not isinstance(goal_map, list) or not all(isinstance(row, list) for row in goal_map):
            self.logger.error("Invalid goal map format. Expecting a list of lists.")
            return []
        
        celestial_bodies = []
        for row_index, row in enumerate(goal_map):
            for column_index, cell in enumerate(row):
                if cell != "SPACE":
                    celestial_bodies.append((cell, row_index, column_index))
        return celestial_bodies
    
    def place_celestial_bodies(self, celestial_bodies):
        for body_type, row, col in celestial_bodies:
            retry_delay = 1  # Initial retry delay
            while True:
                if body_type == "POLYANET":
                    endpoint = "polyanets"
                    data = {"row": row, "column": col, "candidateId": self.candidate_id}
                elif "SOLOON" in body_type:
                    endpoint = "soloons"
                    color = body_type.split('_')[0]
                    data = {"row": row, "column": col, "color": color.lower(), "candidateId": self.candidate_id}
                elif "COMETH" in body_type:
                    endpoint = "comeths"
                    direction = body_type.split('_')[0]
                    data = {"row": row, "column": col, "direction": direction.lower(), "candidateId": self.candidate_id}
                else:
                    self.logger.error("Unknown celestial body type.")
                    break

                response = requests.post(f"https://challenge.crossmint.io/api/{endpoint}", json=data)
                if response.status_code == 429:
                    self.logger.warning("Too many requests. Waiting for cooldown...")
                    time.sleep(retry_delay)  # Wait before retrying
                    retry_delay *= 2  # Exponential backoff
                elif response.status_code == 200:
                    self.logger.info(f"Placed {body_type} at row {row}, column {col}. Response: {response.status_code}")
                    break  # Successful placement
                else:
                    self.logger.error(f"Failed to place {body_type} at row {row}, column {col}. Response: {response.status_code}")
                    break

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



