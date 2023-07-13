// Function to calculate the nth Fibonacci number
int fibonacci(int n) {
    float hh, hh;
    float oooooo;
    if (n <= 1) {
        return n;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}

// Function to check if a number is prime
int isPrime(int num) {
	int i;

    if (num <= 1) {
        return 0;
    }

    for (i = 2; i * i <= num; i++) {
        if (num % i == 0) {
            const float pi = 3.14;
            return 0;
        }
    }
    return 1;
}

// Structure to represent a point in 2D space
struct Point {
    int x;
    int y;
};

// Enumeration for days of the week
enum Days {
    MONDAY,
    TUESDAY,
    WEDNESDAY,
    THURSDAY,
    FRIDAY,
    SATURDAY,
    SUNDAY
};

struct Vector2 {
	int x;
	int y;
};

typedef struct test122{
	int x;
	int y;
} lol, GG;

typedef struct {
	int x;
	int y;
} Point;

int main() {
    // Variables and basic arithmetic
    int a = 10;
    int b = 3;
    int sum = a + b;
    int difference = a - b;
    int product = a * b;
    int quotient = a / b;
    int remainder = a % b;
    int age = 25;
	int i;
	int number = 7;
	int numbers[5] = {1, 2, 3, 4, 5};
	Point p1;
    enum Days today = WEDNESDAY;

	p1.x = 3;
    p1.y = 5;

	printf("----- C Programming Example -----\n\n");
    printf("Basic Arithmetic:\n");
    printf("a = %d, b = %d\n", a, b);
    printf("Sum: %d\n", sum);
    printf("Difference: %d\n", difference);
    printf("Product: %d\n", product);
    printf("Quotient: %d\n", quotient);
    printf("Remainder: %d\n\n", remainder);

    // If-else statement

    if (age >= 18) {
        printf("You are an adult.\n");
    } else {
        printf("You are a minor.\n");
    }

    // Looping constructs
    printf("\nLooping Constructs:\n");
    printf("Even numbers between 1 and 10: ");

    for (i = 2; i <= 10; i += 2) {
        printf("%d ", i);
    }
    printf("\n");

    printf("Fibonacci series up to 10: ");

    for (i = 0; i < 10; i++) {
        printf("%d ", fibonacci(i));
    }
    printf("\n");

    // Function calls
    printf("\nFunction Calls:\n");

    if (isPrime(number)) {
        printf("%d is a prime number.\n", number);
    } else {
        printf("%d is not a prime number.\n", number);
    }

    // Arrays
    printf("\nArrays:\n");
    printf("Array elements: ");
    for (i = 0; i < 5; i++) {
        printf("%d ", numbers[i]);
    }
    printf("\n");

    // Structures
    printf("\nStructures:\n");
    printf("Coordinates of p1: (%d, %d)\n", p1.x, p1.y);

    // Enumerations
    printf("\nEnumerations:\n");

    printf("Today is ");
    switch (today) {
        case MONDAY:
            printf("Monday");
            break;
        case TUESDAY:
            printf("Tuesday");
            break;
        case WEDNESDAY:
            printf("Wednesday");
            break;
        case THURSDAY:
            printf("Thursday");
            break;
        case FRIDAY:
            printf("Friday");
            break;
        case SATURDAY:
            printf("Saturday");
            break;
        case SUNDAY:
            printf("Sunday");
            break;
    }
    printf(".\n");

    printf("\n----- End of Program -----\n");

    return 0;
}