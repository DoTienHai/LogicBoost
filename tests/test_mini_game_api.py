"""
Test mini game with seeded database to verify question loading
"""
import pytest
from app import create_app, db
from app.models import Question


@pytest.fixture
def app():
    """Create test app with seeded database."""
    app = create_app()
    app.config['TESTING'] = True
    
    with app.app_context():
        db.create_all()
        
        # Seed test data
        test_question = Question(
            title='Test Question',
            question='What is $2 + 2$?',
            answer='4',
            mode='mini_game',
            difficulty=1,
            time_limit=60,
            explanation='Simple addition: $2 + 2 = 4$'
        )
        db.session.add(test_question)
        db.session.commit()
        
        yield app
        
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Get test client."""
    return app.test_client()


class TestMiniGameAPI:
    """Test mini game API endpoints."""
    
    def test_question_endpoint_returns_valid_json(self, client):
        """Verify /mini_game/question returns valid question JSON."""
        response = client.get('/mini-game/question')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify response structure
        assert 'id' in data
        assert 'title' in data
        assert 'question' in data
        assert data['question'] is not None
        assert len(data['question']) > 0
        
    def test_question_has_required_fields(self, client):
        """Verify question response has all required fields."""
        response = client.get('/mini-game/question')
        data = response.get_json()
        
        required_fields = ['id', 'title', 'question', 'option_a', 'option_b', 'option_c', 'option_d', 'time_limit']
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
    
    def test_question_not_null(self, client):
        """Verify question text is never null or empty."""
        for _ in range(5):  # Multiple requests
            response = client.get('/mini-game/question')
            data = response.get_json()
            
            assert data['question'] is not None, "Question text should not be None"
            assert isinstance(data['question'], str), "Question should be string"
            assert len(data['question']) > 0, "Question should not be empty"
