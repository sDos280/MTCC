 for (i = 0; i < 5; i += 1)
{
	i -= 1;
}

do {
	i += 1;
} while (i < 5);

switch (choice) {
	case 1:
        break;

	case 2:
		break;
}

{
    int number, i;
    unsigned long long factorial = 1;

    printf("Enter a positive integer: ");
    scanf("%d", &number);

    // Error handling for negative numbers
    if (number < 0) {
        printf("Error: Factorial of a negative number is undefined.\n");
        return 1;
    }

    for (i = 1; i <= number; i++) {
        factorial *= i;
    }

    printf("The factorial of %d is %llu.\n", number, factorial);

    return 0;
}