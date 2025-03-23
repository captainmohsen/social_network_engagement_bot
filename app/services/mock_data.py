mock_follower_data = {
    "Instagram": {
        "test_user": 1600,
        "test_user1": 1020,
        "test_user2": 5000
    },
    "Twitter": {
        "test_user": 800,
        "test_user1": 1500,
        "test_user2": 7000
    }
}

def get_mock_follower_count(social_media: str, username: str) -> int:
    return mock_follower_data.get(social_media, {}).get(username, 0)
