package main

import (
	"fmt"
	"net"
	"time"
)

var maxID int32 = MR_USER
var sessions = make(map[int32]*Session)

func IsActive() {
	for {
		var allIds []int32
		for id := range sessions {
			allIds = append(allIds, id)
		}
		for _, id := range allIds {
			session, ok := sessions[id]
			if ok && !session.stillActive() {
				fmt.Printf("Time out. Client %v disconnected\n", id)
				delete(sessions, id)
			}
		}
		time.Sleep(100 * time.Millisecond)
	}
}

func processClient(conn net.Conn) {
	defer conn.Close()
	m := new(Message)
	code := m.Receive(conn)
	fmt.Println(m.Header.To, ":", m.Header.From, ":", m.Header.Type, ":", code)

	switch code {

	case MT_INIT:
		maxID++
		session := Session{maxID, m.Data, time.Now(), make(chan *Message, 10)}
		sessions[session.id] = &session
		MessageSend(conn, session.id, MR_BROKER, MT_INIT, "")
		fmt.Printf("Client %v last interaction: %v\n", m.Header.From, session.lastInteraction)

	case MT_EXIT:
		delete(sessions, m.Header.From)
		MessageSend(conn, m.Header.From, MR_BROKER, MT_CONFIRM, "")

	case MT_GETDATA:
		if session, ok := sessions[m.Header.From]; ok {
			session.lastInteraction = time.Now()
			fmt.Printf("Client %v last interaction: %v\n", m.Header.From, session.lastInteraction)
			session.Send(conn)
		}

	case MT_INITSTORAGE:
		session := Session{
			id:              MR_STORAGE,
			name:            m.Data,
			lastInteraction: time.Now(),
			messages:        make(chan *Message, 10),
		}
		sessions[session.id] = &session
		fmt.Println("Storage connected")
		MessageSend(conn, session.id, MR_BROKER, MT_INITSTORAGE, "")
		session.lastInteraction = time.Now()

	default:
		{
			time.Sleep(100 * time.Millisecond)
			if fromSession, ok := sessions[m.Header.From]; ok {
				fromSession.lastInteraction = time.Now()
				if toSession, ok := sessions[m.Header.To]; ok {
					toSession.Add(m)
					fmt.Println("Message delivered successfully")
					toSession.lastInteraction = time.Now()
				} else if m.Header.To == MR_ALL {
					for id, session := range sessions {
						if id != m.Header.From {
							session.lastInteraction = time.Now()
							session.Add(m)
							fmt.Printf("Client %v last interaction: %v\n", m.Header.From, session.lastInteraction)
						}
					}
					fmt.Println("Message delivered successfully")
				} else {
					fmt.Println("Message not delivered")
				}
			}

			break
		}
	}
}

func main() {
	go IsActive()

	l, err := net.Listen("tcp", "127.0.0.1:12435")
	if err != nil {
		fmt.Println("Error:", err.Error())
		return
	}
	defer l.Close()

	for {
		conn, err := l.Accept()
		if err != nil {
			fmt.Println("Error:", err.Error())
			return
		}
		go processClient(conn)
	}
}
