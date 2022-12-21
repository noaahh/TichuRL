from src.Stats import get_confidence_interval_probability, \
    poison_distribution, binomial_distribution, get_confidence_interval_expected_value_poisson

if __name__ == "__main__":
    # Print confidence intervals
    print("Confidence intervals:")
    print(f"Poisson: {get_confidence_interval_expected_value_poisson(6.3, 1000, .95)}")
