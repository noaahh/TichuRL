import math

from scipy import stats

def binomial_distribution(n, p, k):
    """
    Binomial distribution
    :param n: number of trials
    :param p: probability of success
    :param k: number of successes
    :return: probability of k successes
    """
    return stats.binom.pmf(k, n, p)

def poison_distribution(l, k):
    """
    Poison distribution
    :param l: lambda
    :param k: number of successes
    :return: probability of k successes
    """
    return stats.poisson.pmf(k, l)

def get_confidence_interval_probability(p, n, confidence_level=.95):
    """
    Get the confidence interval for a probability with a given confidence level
    :param p: probability
    :param n: number of trials
    :param confidence_level: confidence level
    :return: confidence interval
    """
    # Calculate the confidence interval
    interval = stats.norm.interval(confidence_level, loc=p, scale=math.sqrt(p * (1 - p) / n))

    # Round to 5 decimal places and return
    return round(interval[0], 5), round(interval[1], 5)

def get_confidence_interval_expected_value_poisson(x, n, confidence_level=.95):
    """
    Get the confidence interval for the expected value of a random variable with a given confidence level. Assuming poisson distribution
    :param x: expected value (Lamda of poisson distribution)
    :param n: number of trials
    :param confidence_level: confidence level
    :return: confidence interval
    """
    # Calculate the confidence interval
    interval = stats.norm.interval(confidence_level, loc=x, scale=math.sqrt(x / n))

    # Round to 5 decimal places and return
    return round(interval[0], 5), round(interval[1], 5)