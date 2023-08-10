# Think-Tool

Think Tool models a general thinking process for learning and forming new ideas. It uses AI to mimic the same thought processes for you to compare against or use as inspiration.

## Installation

1. Prerequisites: Install openai and tkinter if needed
2. Step-by-step installation instructions:
Just clone the report_make file. It is self contained.

## Usage

1. Run the program and a window should pop up. 
2. Enter your api_key into the field on top. 
3. You can then import notes from a markdown file or type them into the associated fields. 
4. User generation is intended to always precede AI generation. Try the thinking excersize before clicking the button to learn the most.
5. Buttons take from the field above and generate output according to what goes in their text field.
        *For example: "Generate Hypothesis" takes whatever is in critiques and generates hypotheses to output into the hypotheses text field.
        It is important to note that text fields are not cleared after outputting. This means that the text fields can contain both user and multiple genereated outputs.
6. The generate report button collects all of the text into a formatted report. It also creates a study guide which matches questions to a quality source.
7. The final report can be exported as a markdown file. It is formatted specifically for the Obsidian markdown viewing experience.

## Features

- **Fleeting Notes Text Field**: There is a small text field in the corner where you can enter fleeting unrelated ideas. As you type the ideas will scroll out of sight so they do not disrupt the thinking process.
Don't worry they will be included in the final report at the end.
- **Performance Analytics**: A log of time spent in each section is included in the report. This includes the order of each transistion and the time spent in a section before transition.
A measurement of total time in each section is also included. This data could help you identify patterns of your own thinking.

## Contributing

We welcome contributions! Here's how you can help:

1. **Fork & Clone**: Fork this repository and clone it to your machine.
2. **Make Changes**: Make your changes and commit them with a clear and descriptive message.
3. **Test**: Ensure your changes do not break any existing functionality.
4. **Pull Request**: Create a pull request to this repository.

For more detailed instructions or specific contribution guidelines, please refer to the CONTRIBUTING.md (if you have one).

## Acknowledgements

Open AI for their great library and service
LessWrong community for inspiring this experiment   
