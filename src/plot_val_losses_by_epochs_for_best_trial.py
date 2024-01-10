import matplotlib.pyplot as plt

#read validation losses from the file
val_losses = []
with open("best_trial_validation_losses.txt", "r") as file:
    for line in file:
        try:
            loss = float(line.strip())
            val_losses.append(loss)
        except ValueError:
            #handle the case where the line is not a float (e.g., headers or empty lines)
            continue

#plotting
epochs = range(1, len(val_losses) + 1)
plt.plot(epochs, val_losses, marker='o', linestyle='-', color='b')
plt.title('Validation Loss per Epoch')
plt.xlabel('Epoch')
plt.ylabel('Validation Loss')
plt.grid(True)
plt.show()