#!/bin/bash

# Function to print the menu
print_menu() {
  cat text_art.ini
  echo "1. Print out all-time Top Episodes (from Top 1 to Top 250)"
  echo "2. Print out all Unwatched Episodes (from Top 1 to Top 250)"
  echo "3. Print out Top Episodes by Year"
  echo "4. Update Data"
  echo "5. Exit"
}

# Function to handle option 1: Print out all-time Episodes
print_all_time_episodes() {
  python one_piece.py all_time_episodes
  read -p "Press Enter to continue..."
}

# Function to handle option 2: Print out all unwatched episodes
print_unwatched_episodes() {
  python one_piece.py unwatched_episodes
  read -p "Press Enter to continue..."
}

# Function to handle option 3: Print out Top Episodes by Year
print_top_episodes_by_year() {
  python one_piece.py top_episodes_by_year
  read -p "Press Enter to continue..."
}

# Function to handle option 1: Print out all-time Episodes
update_data() {
  python one_piece.py update_data
  echo "Data Updated!"
  read -p "Press Enter to continue..."
}

# Function to prompt for quitting
prompt_to_quit() {
  read -p "Are you sure you want to quit? (y/n): " answer
  if [ "$answer" == "y" ]; then
    echo "Exiting..."
    exit 0
  fi
}

# Main script
while true; do
  clear
  print_menu
  read -p "Enter your choice (1-5): " choice
  case $choice in
    1)
      print_all_time_episodes
      ;;
    2)
      print_unwatched_episodes
      ;;
    3)
      print_top_episodes_by_year
      ;;
    4)
      update_data
      ;;
    5)
      prompt_to_quit
      ;;
    *)
      echo "Invalid choice. Please try again."
      read -p "Press Enter to continue..."
      ;;
  esac
done