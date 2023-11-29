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
	//fmt.Println(m.Header.To, ":", m.Header.From, ":", m.Header.Type, ":", code)

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

	case MT_GET_FROM_STORAGE:
		{
			if m.Header.From == MR_STOR {
				if sessionTo, ok := sessions[m.Header.To]; ok {
					ms := Message{
						Header: MsgHeader{
							To:   m.Header.To,
							From: MR_BROKER,
							Type: MT_GET_FROM_STORAGE,
							Size: int32(len(m.Data)),
						},
						Data: m.Data,
					}
					sessionTo.Add(&ms)
				}
			} else {
				if sessionFrom, ok := sessions[m.Header.From]; ok {
					if storageSession, ok := sessions[MR_STOR]; ok {
						sessionFrom.lastInteraction = time.Now()
						ms := Message{
							Header: MsgHeader{
								To:   MR_STOR,
								From: m.Header.From,
								Type: MT_GET_FROM_STORAGE,
								Size: 0,
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

			iSessionFrom, fromExists := sessions[m.Header.From]
			storageSession, storageExists := sessions[MR_STOR]

			if fromExists && m.Header.From != MR_STOR {
				iSessionFrom.lastInteraction = time.Now()

				iSessionTo, toExists := sessions[m.Header.To]
				if toExists {
					iSessionTo.Add(m)

					if storageExists {
						m.Data = "{'" + fmt.Sprint(m.Header.From) + "':'" + m.Data + "'}"
						ms := Message{
							Header: MsgHeader{
								To:   MR_BROKER,
								From: m.Header.To,
								Type: MT_DATA,
								Size: int32(len(m.Data)),
							},
							Data: m.Data,
						}
						storageSession.Add(&ms)
					}

					fmt.Println("Message delivered successfully")
					iSessionTo.lastInteraction = time.Now()
				} else if m.Header.To == MR_ALL {
					for id, session := range sessions {
						if id != m.Header.From && id != MR_STOR {
							session.lastInteraction = time.Now()
							session.Add(m)

							if storageExists {
								mes := "{'" + fmt.Sprint(m.Header.From) + "':'" + m.Data + "'}"
								ms := Message{
									Header: MsgHeader{
										To:   MR_BROKER,
										From: id,
										Type: MT_DATA,
										Size: int32(len(mes)),
									},
									Data: mes,
								}
								storageSession.Add(&ms)
							}
						}
					}

					fmt.Println("Message delivered successfully")
				}
			}
			if _, exists := sessions[MT_REST]; exists {
				sessions[MT_REST].Add(m)
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
