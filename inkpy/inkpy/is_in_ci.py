"""
CI Detection - Detect if running in a CI environment
"""
import os


def is_in_ci() -> bool:
    """
    Detect if running in a CI environment.
    
    Checks common CI environment variables.
    
    Returns:
        True if running in CI, False otherwise
    """
    ci_env_vars = [
        'CI',
        'CONTINUOUS_INTEGRATION',
        'BUILD_NUMBER',
        'GITHUB_ACTIONS',
        'GITLAB_CI',
        'CIRCLECI',
        'TRAVIS',
        'JENKINS_URL',
        'TEAMCITY_VERSION',
        'APPVEYOR',
        'BITBUCKET_BUILD_NUMBER',
    ]
    
    return any(os.environ.get(var) for var in ci_env_vars)

