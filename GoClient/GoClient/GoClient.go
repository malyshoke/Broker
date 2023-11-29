package main

import (
	"fmt"
	"time"
)

func ProcessMessages() {
	for {
		m := MessageCall(MR_BROKER, MT_GETDATA, "")
		switch m.Header.Type {
		case MT_DATA:
			fmt.Printf("You got a message: %s\nFrom: %d\n", m.Data, m.Header.From)
		default:
			time.Sleep(time.Millisecond * 100)
		}
	}
}

func main() {
	MessageCall(MR_BROKER, MT_INIT, "")

	go ProcessMessages()

	for {
		fmt.Println("Menu:")
		fmt.Println("1. Choose receiver")
		fmt.Println("2. Broadcast message")
		fmt.Println("3. Exit")

		var number int
		fmt.Print("Enter your choice: ")
		_, err := fmt.Scanf("%d", &number)
		if err != nil {
			fmt.Println("Error reading input:", err)
			return
		}

		fmt.Scanln()
		switch number {
		case 1:
			fmt.Print("Enter receiver's id: ")
			var to int32
			_, err := fmt.Scanf("%d", &to)
			if err != nil {
				fmt.Println("Error reading input:", err)
				return
			}
			fmt.Scanln()
			fmt.Print("Enter your message: ")
			var str string
			fmt.Scanln(&str)
			MessageCall(to, MT_DATA, str)
		case 2:
			fmt.Scanln()
			fmt.Print("Enter your message: ")
			var str string
			fmt.Scanln(&str)
			MessageCall(MR_ALL, MT_DATA, str)
		case 3:
			MessageCall(MR_BROKER, MT_EXIT, "")
			return
		default:
			fmt.Println("Invalid choice. Please enter a valid option.")
		}
	}
}
