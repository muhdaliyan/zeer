#!/usr/bin/env python3
"""
zeer CLI - Main Entry Point

This is the main entry point for the zeer CLI application.
It instantiates the AppController and handles top-level exceptions and cleanup.

Requirements: 1.1, 8.2
"""

import sys
import argparse
from src.app_controller import AppController


def main():
    """
    Main entry point for zeer CLI.
    
    Instantiates the AppController, runs the application, and handles
    top-level exceptions and cleanup.
    
    Requirements: 1.1, 8.2
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Zeer - Agentic AI CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  zeer                    Start a new chat session
  zeer chat <session-id>  Resume a saved chat session
        """
    )
    parser.add_argument(
        'command',
        nargs='?',
        choices=['chat'],
        help='Command to execute'
    )
    parser.add_argument(
        'session_id',
        nargs='?',
        help='Session ID to resume (use with "chat" command)'
    )
    
    args = parser.parse_args()
    
    try:
        # Instantiate the application controller
        app = AppController()
        
        # Check if user wants to resume a session
        if args.command == 'chat' and args.session_id:
            app.run(resume_session_id=args.session_id)
        else:
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
