from src.Stats import get_confidence_interval_probability, get_confidence_interval_expected_value, \
    poison_distribution, binomial_distribution

if __name__ == "__main__":
    # Print confidence intervals
    print("Confidence intervals:")
    print(f"Probability: {get_confidence_interval_probability(0.5, 1000)}")
    print(f"Expected value: {get_confidence_interval_expected_value(0.5, 1000)}")

    # Print poison distribution
    print("Poison distribution:")
    print(f"p: {poison_distribution(0.5, 0)}")

    # Print binomial distribution
    print("Binomial distribution:")
    print(f"p: {binomial_distribution(1000, 0.5, 0)}")
