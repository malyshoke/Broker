package main

import (
	"fmt"
	"time"
)

func main() {
	MessageCall(MR_BROKER, MT_INIT, "")
	go func() {
		for {
			m := MessageCall(MR_BROKER, MT_GETDATA, "")
			if m.Header.Type == MT_DATA {
				fmt.Println(m.Data)
			} else {
				time.Sleep(time.Second * 1)
			}
		}
	}()
	for {
		var s string
		fmt.Scanln(&s)
		MessageCall(MR_ALL, MT_DATA, s)
	}
}
