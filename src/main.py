#!/usr/bin/env python3
"""
zeer CLI - Main Entry Point

This is the main entry point for the zeer CLI application.
It instantiates the AppController and handles top-level exceptions and cleanup.

Requirements: 1.1, 8.2
"""

import sys
from src.app_controller import AppController


def main():
    """
    Main entry point for zeer CLI.
    
    Instantiates the AppController, runs the application, and handles
    top-level exceptions and cleanup.
    
    Requirements: 1.1, 8.2
    """
    try:
        # Instantiate and run the application controller
        app = AppController()
        app.run()
        
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\n\nInterrupted. Exiting zeer...")
        sys.exit(0)
        
    except Exception as e:
        # Handle any unexpected top-level exceptions
        print(f"\n\nFatal error: {str(e)}", file=sys.stderr)
        sys.exit(1)
        
    finally:
        # Ensure cleanup happens
        # The AppController's run() method already handles session cleanup
        # in its finally block, but we ensure a clean exit here
        pass


if __name__ == "__main__":
    main()
