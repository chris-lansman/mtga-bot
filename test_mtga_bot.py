"""
Unit tests for MTGA Bot.

Run with: python -m pytest test_mtga_bot.py
or: python -m unittest test_mtga_bot.py
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock win32gui before importing the main module
sys.modules['win32gui'] = MagicMock()

import mtga_bot_image_rec as bot
from windowed_mode import get_window_rez, get_mtga_window_corners


class TestExtractText(unittest.TestCase):
    """Test text extraction functionality."""
    
    @patch('mtga_bot_image_rec.ImageGrab.grab')
    @patch('mtga_bot_image_rec.pytesseract.image_to_string')
    def test_extract_text_basic(self, mock_tesseract, mock_grab):
        """Test basic text extraction."""
        # Setup mocks
        mock_img = MagicMock()
        mock_img.size = (100, 50)
        mock_img.getpixel.return_value = 200
        mock_grab.return_value = mock_img
        mock_tesseract.return_value = "play"
        
        # Test
        result = bot.extract_text((0, 0, 100, 50), threshold=235)
        
        # Verify
        self.assertEqual(result, "play")
        mock_grab.assert_called_once()
    
    @patch('mtga_bot_image_rec.ImageGrab.grab')
    def test_extract_text_error_handling(self, mock_grab):
        """Test that extract_text handles errors gracefully."""
        mock_grab.side_effect = Exception("Screen capture failed")
        
        # Should return empty string on error
        result = bot.extract_text((0, 0, 100, 50))
        self.assertEqual(result, "")


class TestCoordinateScaling(unittest.TestCase):
    """Test coordinate scaling for different resolutions."""
    
    def test_get_window_rez(self):
        """Test window resolution calculation."""
        # Test standard 1920x1080
        coords = (0, 0, 1920, 1080)
        rez = get_window_rez(coords)
        self.assertEqual(rez, (1900, 1000))
        
        # Test 1280x720
        coords = (0, 0, 1280, 720)
        rez = get_window_rez(coords)
        self.assertEqual(rez, (1200, 700))


class TestGameStateDetection(unittest.TestCase):
    """Test game state detection logic."""
    
    @patch('mtga_bot_image_rec.extract_text')
    def test_scan_screen_start_state(self, mock_extract):
        """Test detection of start screen."""
        # Mock text extraction to return start screen indicators
        mock_extract.side_effect = ['play', '', '']
        
        result = bot.scan_screen_for_text()
        self.assertEqual(result, "Start")
    
    @patch('mtga_bot_image_rec.extract_text')
    def test_scan_screen_in_match(self, mock_extract):
        """Test detection of in-match state."""
        # Mock text extraction to return match indicators
        def side_effect(*args):
            return ''
        
        # Setup to return 'keep' when checking for match
        calls = ['', '', '', '', 'keep']
        mock_extract.side_effect = calls
        
        result = bot.scan_screen_for_text()
        self.assertEqual(result, "In Match")


class TestClickFunctions(unittest.TestCase):
    """Test mouse click functions."""
    
    @patch('mtga_bot_image_rec.pyautogui.mouseDown')
    @patch('mtga_bot_image_rec.pyautogui.mouseUp')
    def test_leftClick(self, mock_up, mock_down):
        """Test left click function."""
        bot.leftClick((100, 200))
        
        mock_down.assert_called_once_with(x=100, y=200)
        mock_up.assert_called_once_with(x=100, y=200)
    
    @patch('mtga_bot_image_rec.pyautogui.doubleClick')
    def test_doubleLeftClick(self, mock_double):
        """Test double left click function."""
        bot.doubleLeftClick((150, 250))
        
        mock_double.assert_called_once_with(x=150, y=250, interval=0.25)
    
    def test_leftClick_disabled(self):
        """Test that clicks are disabled when CLICKS_DISABLED is True."""
        original = bot.CLICKS_DISABLED
        bot.CLICKS_DISABLED = True
        
        with patch('mtga_bot_image_rec.pyautogui.mouseDown') as mock_down:
            bot.leftClick((100, 200))
            mock_down.assert_not_called()
        
        bot.CLICKS_DISABLED = original


class TestWindowManagement(unittest.TestCase):
    """Test window management functions."""
    
    @patch('mtga_bot_image_rec.win32gui.FindWindow')
    @patch('mtga_bot_image_rec.win32gui.GetWindowRect')
    @patch('mtga_bot_image_rec.win32gui.SetWindowPos')
    def test_check_mtga_window_size(self, mock_set, mock_get, mock_find):
        """Test MTGA window size checking and adjustment."""
        mock_find.return_value = 12345  # Mock window handle
        mock_get.return_value = (100, 100, 1820, 1180)  # Wrong size
        
        result = bot.check_mtga_window_size()
        
        # Should call SetWindowPos to adjust window
        mock_set.assert_called_once()
        self.assertTrue(result)
    
    @patch('mtga_bot_image_rec.win32gui.FindWindow')
    def test_check_mtga_window_not_found(self, mock_find):
        """Test handling when MTGA window is not found."""
        mock_find.return_value = None
        
        result = bot.check_mtga_window_size()
        self.assertFalse(result)


class TestTurnPhaseDetection(unittest.TestCase):
    """Test turn phase detection."""
    
    @patch('mtga_bot_image_rec.extract_text')
    def test_turn_phase_play_cards(self, mock_extract):
        """Test detection of play cards phase."""
        mock_extract.side_effect = ['next', 'combat']
        
        result = bot.turn_phase()
        self.assertEqual(result, "play cards")
    
    @patch('mtga_bot_image_rec.extract_text')
    def test_turn_phase_attack(self, mock_extract):
        """Test detection of attack phase."""
        mock_extract.side_effect = ['', '', '', 'no attacks', 'all attack']
        
        result = bot.turn_phase()
        self.assertEqual(result, "attack phase")


class TestCordClass(unittest.TestCase):
    """Test Cord class coordinate definitions."""
    
    def test_cord_coordinates_valid(self):
        """Test that Cord class has valid coordinate tuples."""
        # Check that coordinates are tuples of length 2
        self.assertEqual(len(bot.Cord.play_button), 2)
        self.assertEqual(len(bot.Cord.keep_draw_button), 2)
        self.assertEqual(len(bot.Cord.cancel_button), 2)
        
        # Check that coordinates are positive integers
        self.assertGreater(bot.Cord.play_button[0], 0)
        self.assertGreater(bot.Cord.play_button[1], 0)
    
    def test_cards_in_hand_tuple(self):
        """Test that cards_in_hand is a valid tuple of coordinates."""
        self.assertIsInstance(bot.Cord.cards_in_hand, tuple)
        self.assertGreater(len(bot.Cord.cards_in_hand), 0)
        
        # Check first card coordinate
        first_card = bot.Cord.cards_in_hand[0]
        self.assertEqual(len(first_card), 2)
        self.assertGreater(first_card[0], 0)
        self.assertGreater(first_card[1], 0)


class TestTextLocationDictionary(unittest.TestCase):
    """Test text_loc_dict configuration."""
    
    def test_text_loc_dict_structure(self):
        """Test that text_loc_dict has valid structure."""
        # Check that dictionary is not empty
        self.assertGreater(len(bot.text_loc_dict), 0)
        
        # Check that all values are tuples of length 4
        for key, value in bot.text_loc_dict.items():
            with self.subTest(key=key):
                self.assertIsInstance(value, tuple)
                self.assertEqual(len(value), 4, f"Key '{key}' should have 4 coordinates")
                
                # Check that coordinates are in correct order (x1, y1, x2, y2)
                x1, y1, x2, y2 = value
                self.assertLess(x1, x2, f"Key '{key}': x1 should be less than x2")
                self.assertLess(y1, y2, f"Key '{key}': y1 should be less than y2")
    
    def test_text_loc_dict_required_keys(self):
        """Test that text_loc_dict has required keys."""
        required_keys = ['play', 'home', 'keep', 'mulligan', 'cancel', 'next', 'pass']
        
        for key in required_keys:
            with self.subTest(key=key):
                self.assertIn(key, bot.text_loc_dict, f"Missing required key: {key}")


if __name__ == '__main__':
    unittest.main()

