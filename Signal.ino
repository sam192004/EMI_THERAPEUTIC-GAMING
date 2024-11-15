#define SAMPLE_RATE 1000
#define BAUD_RATE 9600
#define INPUT_PIN A0
#define BUFFER_SIZE 128

// Circular buffer and related variables
int circular_buffer[BUFFER_SIZE] = {0}; // Initialize buffer with zeros
int data_index = 0;
int sum = 0;

void setup() {
    // Initialize the serial connection
    Serial.begin(BAUD_RATE);
}

void loop() {
    // Calculate elapsed time
    static unsigned long past = 0;
    unsigned long present = micros();
    unsigned long interval = present - past;

    // Timer logic
    static long timer = 0;
    timer -= interval;
    past = present;

    // Sample and process signal
    if (timer < 0) {
        timer += 1000000 / SAMPLE_RATE;

        int sensor_value = analogRead(INPUT_PIN);
        float signal = EMGFilter((float)sensor_value); // Cast to float for filter
        int envelope = getEnvelope(abs(signal));

        // Print signal and envelope to serial
        Serial.print(signal, 2); // Print with two decimal places
        Serial.print(",");
        Serial.println(envelope);
    }
}

// Envelope detection using a circular buffer
int getEnvelope(int abs_emg) {
    sum -= circular_buffer[data_index]; // Subtract the old value
    sum += abs_emg;                     // Add the new value
    circular_buffer[data_index] = abs_emg; // Store the new value in the buffer

    data_index = (data_index + 1) % BUFFER_SIZE; // Update circular buffer index
    return (sum / BUFFER_SIZE) * 2; // Scale by 2 (adjust if needed)
}

// EMG signal filtering using cascaded filters
float EMGFilter(float input) {
    float output = input;

    // First filter section
    {
        static float z1 = 0, z2 = 0; // Initialize filter state
        float x = output - 0.05159732 * z1 - 0.36347401 * z2;
        output = 0.01856301 * x + 0.03712602 * z1 + 0.01856301 * z2;
        z2 = z1;
        z1 = x;
    }

    // Second filter section
    {
        static float z1 = 0, z2 = 0; // Initialize filter state
        float x = output - -0.53945795 * z1 - 0.39764934 * z2;
        output = 1.00000000 * x + -2.00000000 * z1 + 1.00000000 * z2;
        z2 = z1;
        z1 = x;
    }

    // Third filter section
    {
        static float z1 = 0, z2 = 0; // Initialize filter state
        float x = output - 0.47319594 * z1 - 0.70744137 * z2;
        output = 1.00000000 * x + 2.00000000 * z1 + 1.00000000 * z2;
        z2 = z1;
        z1 = x;
    }

    // Fourth filter section
    {
        static float z1 = 0, z2 = 0; // Initialize filter state
        float x = output - -1.00211112 * z1 - 0.74520226 * z2;
        output = 1.00000000 * x + -2.00000000 * z1 + 1.00000000 * z2;
        z2 = z1;
        z1 = x;
    }

    return output;
}
