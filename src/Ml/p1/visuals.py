###########################################
# Supplementary visualisation helpers for the Boston Housing project.
# Updated for modern scikit-learn (>= 0.20) and matplotlib.
###########################################
import warnings

import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import ShuffleSplit, train_test_split, validation_curve
from sklearn.tree import DecisionTreeRegressor

# Suppress matplotlib user warnings (needed for newer matplotlib versions)
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")


def ModelComplexity(X, y):
    """Calculates the performance of the model as model complexity increases.
    The training and validation scores are then plotted."""

    # Create 10 cross-validation sets for training and testing
    cv = ShuffleSplit(n_splits=10, test_size=0.2, random_state=0)

    # Vary the max_depth parameter from 1 to 10
    max_depth = np.arange(1, 11)

    # Calculate the training and testing scores
    train_scores, test_scores = validation_curve(
        DecisionTreeRegressor(random_state=0), X, y,
        param_name="max_depth", param_range=max_depth, cv=cv, scoring="r2",
    )

    # Find the mean and standard deviation for smoothing
    train_mean = np.mean(train_scores, axis=1)
    train_std = np.std(train_scores, axis=1)
    test_mean = np.mean(test_scores, axis=1)
    test_std = np.std(test_scores, axis=1)

    # Plot the validation curve
    plt.figure(figsize=(7, 5))
    plt.title("Decision Tree Regressor Complexity Performance")
    plt.plot(max_depth, train_mean, "o-", color="r", label="Training Score")
    plt.plot(max_depth, test_mean, "o-", color="g", label="Validation Score")
    plt.fill_between(max_depth, train_mean - train_std,
                     train_mean + train_std, alpha=0.15, color="r")
    plt.fill_between(max_depth, test_mean - test_std,
                     test_mean + test_std, alpha=0.15, color="g")

    # Visual aesthetics
    plt.legend(loc="lower right")
    plt.xlabel("Maximum Depth")
    plt.ylabel("Score")
    plt.ylim([-0.05, 1.05])
    plt.show()


def PredictTrials(X, y, fitter, data):
    """Performs trials of fitting and predicting data."""

    # Work on plain arrays so that no feature-name warnings are raised
    X = np.asarray(X)
    y = np.asarray(y)

    # Store the predicted prices
    prices = []

    for k in range(10):
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=k)

        # Fit the data
        reg = fitter(X_train, y_train)

        # Make a prediction
        pred = reg.predict([data[0]])[0]
        prices.append(pred)

        # Result
        print("Trial {}: ${:,.2f}".format(k + 1, pred))

    # Display price range
    print("\nRange in prices: ${:,.2f}".format(max(prices) - min(prices)))
