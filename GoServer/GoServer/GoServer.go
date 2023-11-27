package main

import (
	"fmt"
	"net"
	"time"
)

var maxID int32 = MR_USER
var sessions = make(map[int32]Session)

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

	switch code {
	case MT_INIT:
		maxID++
		session := Session{maxID, m.Data, time.Now(), make(chan *Message, 10)}
		sessions[session.id] = session
		MessageSend(conn, session.id, MR_BROKER, MT_INIT, "")
		fmt.Printf("Client %v last interaction: %v\n", m.Header.From, session.lastInteraction)

	case MT_EXIT:
		delete(sessions, m.Header.From)
		fmt.Printf("Client %v disconnected\n", m.Header.From)

	case MT_GETDATA:
		if session, ok := sessions[m.Header.From]; ok {
			session.lastInteraction = time.Now()
			fmt.Printf("Client %v last interaction: %v\n", m.Header.From, session.lastInteraction)
			session.Send(conn)
		} else {

		}

	case MT_GETLAST:
		{
			if m.Header.From == MR_STORAGE {
				if sessionTo, ok := sessions[m.Header.To]; ok {
					ms := Message{
						Header: MsgHeader{
							To:   m.Header.To,
							From: MR_BROKER,
							Type: MT_GETLAST,
							Size: int32(len(m.Data)),
						},
						Data: m.Data,
					}
					sessionTo.Add(&ms)
				}
			} else {
				if sessionFrom, ok := sessions[m.Header.From]; ok {
					if storageSession, ok := sessions[MR_STORAGE]; ok {
						sessionFrom.lastInteraction = time.Now()
						ms := Message{
							Header: MsgHeader{
								To:   MR_STORAGE,
								From: m.Header.From,
								Type: MT_GETLAST,
								Size: 0, // или другое значение размера
							},
							Data: "",
						}
						storageSession.Add(&ms)
					}
				}
			}
			break
		}

	default:
		{
			time.Sleep(100 * time.Millisecond)
			if fromSession, ok := sessions[m.Header.From]; ok {
				fromSession.lastInteraction = time.Now()
				fmt.Printf("Client %v last interaction: %v\n", m.Header.From, fromSession.lastInteraction)

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
			} else {
			}
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
