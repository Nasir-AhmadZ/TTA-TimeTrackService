from app import consumer

def test_initial_current_user():
    """Test that currentUser has default value"""
    assert consumer.currentUser == "691c8bf8d691e46d00068bf3"