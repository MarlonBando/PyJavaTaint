import java.util.Scanner;

public class UserInputs {
    private Scanner scanner;

    // Constructor initializes the Scanner
    public UserInputs() {
        this.scanner = new Scanner(System.in);
    }

    // Method to get user input
    public String getInput() {
        System.out.print("Please enter your input: ");
        String input = scanner.nextLine();
        return input;
    }

    // Method to get input with a custom prompt
    public String getInput(String prompt) {
        System.out.print(prompt);
        String input = scanner.nextLine();
        return input;
    }

    // Clean up resources
    public void closeScanner() {
        if (scanner != null) {
            scanner.close();
        }
    }

    public static void main(String[] args) {
        UserInputs userInputs = new UserInputs();
        String userInput = userInputs.getInput();
        System.out.println("You entered: " + userInput);
        userInputs.closeScanner();
    }
}