# LangChain Agents Project

This project demonstrates the use of LangChain agents with custom tools for various tasks.

## Project Structure

- `agent.py`: Implements a LangChain agent with tools for number extraction, calculating averages, and comparing numbers. It also logs tool usage.
- `cyclingagent.py`: Implements a LangChain agent with tools for cycling-related calculations, including distance between Bengaluru and Mysore (hardcoded coordinates), estimated calories burned, and estimated cycling time. This agent utilizes the `openrouteservice` library.
- `requirements.txt`: Lists the Python dependencies required for the project.
- `.env`: (Not committed) Used to store API keys for secure access.

## Installation

1.  **Clone the repository (if applicable):**
    ```bash
    git clone <repository_url>
    cd langchainagents
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv langchainagents
    ```

3.  **Activate the virtual environment:**
    -   **Windows:**
        ```bash
        .\langchainagents\Scripts\activate
        ```
    -   **macOS/Linux:**
        ```bash
        source ./langchainagents/bin/activate
        ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

Create a `.env` file in the root directory of the project (`D:/langchainagents/`) and add your API keys:

```dotenv
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
ORS_API_KEY="YOUR_OPENROUTESERVICE_API_KEY"
```

-   **`GEMINI_API_KEY`**: Obtain this from Google AI Studio or Google Cloud.
-   **`ORS_API_KEY`**: Obtain this from the OpenRouteService website.

## Usage

### Running `agent.py`

This agent can extract numbers, calculate their average, and compare a given number with the stored average.

```bash
python agent.py
```

Follow the prompts in the console to interact with the agent.

### Running `cyclingagent.py`

This agent provides cycling-related information, such as distance between Bengaluru and Mysore, calorie estimation, and time estimation.

```bash
python cyclingagent.py
```

Follow the prompts in the console to ask cycling-related questions.
