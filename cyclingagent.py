from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, Tool
import openrouteservice

load_dotenv()

llm = ChatGoogleGenerativeAI(
    google_api_key=os.getenv("GEMINI_API_KEY"),
    model="gemini-2.0-flash",
    max_output_tokens=2048,
    temperature=0.2,
)

# Tool 1: Get cycling distance between Bengaluru and Mysore using hardcoded coordinates
class CyclingDistanceTool:
    def run(self, query: str) -> str:
        api_key = os.getenv("ORS_API_KEY")
        if not api_key:
            return "OpenRouteService API key not set."
        # Hardcoded coordinates for Bengaluru and Mysore
        coords = [
            (77.5775, 12.9629),  # Bengaluru (longitude, latitude)
            (76.6394, 12.2958)   # Mysore (longitude, latitude)
        ]
        try:
            client = openrouteservice.Client(key=api_key)
            routes = client.directions(coords)
            distance_meters = routes['routes'][0]['summary']['distance']
            distance_km = distance_meters / 1000
            return f"{distance_km:.2f} kilometers"
        except Exception as e:
            return f"Error fetching cycling distance: {str(e)}"

# Tool 2: Calculate calories burned cycling
class CyclingCaloriesTool:
    def run(self, query: str) -> str:
        # Example: "70kg, 150 kilometers"
        import re
        match = re.match(r"(\d+)\s*kg.*?([\d\.]+)\s*kilometers", query.lower())
        if not match:
            return "Please provide input in the format: '<weight>kg, <distance> kilometers'"
        weight = float(match.group(1))
        distance = float(match.group(2))
        # Standard estimate: calories = weight(kg) * distance(km) * 0.28 (cycling moderate)
        calories = weight * distance * 0.28
        return f"You will burn approximately {calories:.0f} calories cycling {distance} km at {weight} kg."

# Tool 3: Estimate cycling time (assuming average speed)
class CyclingTimeTool:
    def run(self, query: str) -> str:
        # Example: "150 kilometers at 20 km/h"
        import re
        match = re.match(r"([\d\.]+)\s*kilometers.*?([\d\.]+)\s*km/?h", query.lower())
        if not match:
            return "Please provide input in the format: '<distance> kilometers at <speed> km/h'"
        distance = float(match.group(1))
        speed = float(match.group(2))
        if speed == 0:
            return "Speed must be greater than zero."
        hours = distance / speed
        return f"Estimated cycling time: {hours:.2f} hours at {speed} km/h for {distance} km."

cycling_distance_tool = Tool(
    name="Cycling Distance",
    func=CyclingDistanceTool().run,
    description="Gets the cycling route distance in kilometers between Bengaluru and Mysore."
)

cycling_calories_tool = Tool(
    name="Cycling Calories Calculator",
    func=CyclingCaloriesTool().run,
    description="Estimates calories burned cycling. Example: '70kg, 150 kilometers'."
)

cycling_time_tool = Tool(
    name="Cycling Time Estimator",
    func=CyclingTimeTool().run,
    description="Estimates cycling time given distance and speed. Example: '150 kilometers at 20 km/h'."
)

tools = [cycling_distance_tool, cycling_calories_tool, cycling_time_tool]

agent = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=True
)

# query = "What is the cycling distance from Bengaluru to Mysore? If I weigh 70kg, how many calories will I burn cycling that distance? How long will it take if I cycle that distance at 20 km/h?"


if __name__ == "__main__":
    while True:
        user_input = input("Ask your cycling question (or type 'exit' to quit): ")
        if user_input.strip().lower() == "exit":
            break
        result = agent.invoke(user_input)
        print(result)