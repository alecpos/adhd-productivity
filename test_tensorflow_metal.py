import tensorflow as tf

# Print TensorFlow version
print(f"TensorFlow version: {tf.__version__}")

# List available devices
print("\nAvailable devices:")
for device in tf.config.list_physical_devices():
    print(device)

# Create a simple model to test Metal
print("\nTesting Metal device with a simple model:")
try:
    # Create a simple model
    model = tf.keras.Sequential(
        [
            tf.keras.layers.Dense(128, activation="relu", input_shape=(784,)),
            tf.keras.layers.Dense(10, activation="softmax"),
        ]
    )

    # Compile the model
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])

    # Generate some dummy data
    x_train = tf.random.normal((1000, 784))
    y_train = tf.random.uniform((1000,), minval=0, maxval=10, dtype=tf.int32)

    # Train the model
    history = model.fit(x_train, y_train, epochs=1, verbose=1)
    print("\nTraining completed successfully!")

except Exception as e:
    print(f"\nError occurred: {str(e)}")
