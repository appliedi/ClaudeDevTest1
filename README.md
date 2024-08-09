# Rotary International Grant Calculator

## Introduction

The Rotary International Grant Calculator is a Streamlit-based web application designed to help Rotary clubs and districts plan and calculate funding for Global Grant projects. This tool simplifies the complex process of determining contributions, matching funds, and total project funding while ensuring compliance with Rotary International's funding rules.

## Features

- Dynamic input for Host Clubs, International Clubs, and Other Donors
- Automatic calculation of total contributions and World Fund match
- Validation of funding structure based on Rotary International rules
- Generation of detailed PDF reports
- Interactive funding breakdown visualization
- Project data saving and loading functionality

## Installation

1. Ensure you have Python 3.7 or later installed on your system.
2. Clone this repository to your local machine:
   ```
   git clone https://github.com/your-username/rotary-grant-calculator.git
   cd rotary-grant-calculator
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the Streamlit app:
   ```
   streamlit run global_grant_calculator.py
   ```
2. Open a web browser and navigate to `http://localhost:8501` (or the provided Network URL if accessing from another device).
3. Use the interface to input project details:
   - Enter the Application # and Project Country
   - Add Host Clubs, International Clubs, and Other Donors as needed using the "Add" buttons
   - Input the Endowed/Directed Gift information if applicable
4. Click "Calculate and Generate PDF" to view the results and download a detailed report
5. Use the "Save Project Data" button to save your project for future reference
6. Use the "Load Project Data" feature to resume work on a saved project

## Funding Structure

The calculator takes into account the following funding components:

- **DDF (District Designated Fund)**: Allocated by Rotary districts
- **Cash Contributions**:
  - Cash Direct to Project: Contributed directly to the project
  - Cash through TRF: Contributed through The Rotary Foundation (subject to a 5% fee)
- **World Fund Match**: 80% of total DDF contributions, up to $400,000
- **Other Donors**: Additional contributions from non-Rotary sources
- **Endowed/Directed Gift**: Special contributions treated as project cash

## Key Rules

- International partner contributions must be at least 15% of the total
- Total funding must be at least $30,000
- Non-Rotarian contributions cannot come from a cooperating organization or a project beneficiary

## Contributing

Contributions to improve the Rotary International Grant Calculator are welcome. Please feel free to submit pull requests or open issues to suggest improvements or report bugs.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Rotary International for their commitment to global humanitarian projects
- The Streamlit team for their excellent framework for building data apps

For more information about Rotary Global Grants, visit [Rotary International's website](https://www.rotary.org/en/our-programs/grants).