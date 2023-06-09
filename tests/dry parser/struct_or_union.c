union Data {
    int i;
    float f;
    char c;
};

struct Book {
    int bookID;
    float price;
    char title[50], title2;
};

struct Rectangle {
    struct Point topLeft;
    struct Point bottomRight;
};

struct Employee {
    char name[50];
    union {
        int employeeID;
        float salary;
    } info;
};

struct DataValue {
    enum DataType {
	    INT,
	    FLOAT,
	    STRING
	} type;

    union {
        int intValue;
        float floatValue;
        char stringValue[50];
    } value;
};


