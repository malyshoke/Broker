package main

import (
	"fmt"
	"net"
	"strconv"
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

	case MT_GETLAST_PUBLIC:
		{
			if m.Header.From == MR_STORAGE {
				if sessionTo, ok := sessions[m.Header.To]; ok {
					ms := Message{
						Header: MsgHeader{
							To:   m.Header.To,
							From: MR_BROKER,
							Type: MT_GETLAST_PUBLIC,
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
								Type: MT_GETLAST_PUBLIC,
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

	case MT_INITSTORAGE:
		{
			session := Session{
				id:              MR_STORAGE,
				name:            m.Data,
				lastInteraction: time.Now(),
				messages:        make(chan *Message, 10),
			}
			sessions[session.id] = session
			fmt.Println("Storage connected")
			MessageSend(conn, session.id, MR_BROKER, MT_INITSTORAGE, "")
			session.lastInteraction = time.Now()
			break
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

	case MT_REST:
		{
			session := Session{
				id:              MR_RESTSERVER,
				name:            m.Data,
				lastInteraction: time.Now(),
				messages:        make(chan *Message, 10),
			}
			sessions[session.id] = session
			fmt.Println("Rest connected")
			MessageSend(conn, session.id, MR_BROKER, MT_REST, "")
			session.lastInteraction = time.Now()
			break
		}

	default:
		time.Sleep(100 * time.Millisecond)
		iSessionFrom, fromSessionExists := sessions[m.Header.From]
		StorageSession, storageExists := sessions[MR_STORAGE]

		if fromSessionExists && m.Header.From != MR_STORAGE {
			iSessionFrom.lastInteraction = time.Now()
			iSessionTo, toSessionExists := sessions[m.Header.To]

			if toSessionExists {
				iSessionTo.Add(m)
				fmt.Println("Message added:", m.Data)
				if storageExists {
					m.Data = "{'" + strconv.Itoa(int(m.Header.From)) + "':'" + m.Data + "'}"
					ms := Message{
						Header: MsgHeader{
							To:   MR_BROKER,
							From: m.Header.To,
							Type: MT_DATA,
							Size: int32(len(m.Data)),
						},
						Data: m.Data,
					}
					StorageSession.Add(&ms)
					fmt.Println(ms.Data)
				}
				fmt.Println("Message delivered successfully")
				iSessionTo.lastInteraction = time.Now()
			} else if m.Header.To == MR_ALL {
				mes := "{'" + strconv.Itoa(int(m.Header.From)) + "':'" + m.Data + "'}"
				fmt.Println(mes)
				for id, session := range sessions {
					if id != m.Header.From && id != MR_STORAGE {
						session.lastInteraction = time.Now()
						session.Add(m)
					}
				}
				if storageExists {
					ms := Message{
						Header: MsgHeader{
							To:   MR_BROKER,
							From: MR_ALL,
							Type: MT_DATA,
							Size: int32(len(mes)),
						},
						Data: mes,
					}
					StorageSession.Add(&ms)
				}
				fmt.Println("Message delivered successfully")
			}
		}
		break
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
