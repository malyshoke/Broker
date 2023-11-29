package main

import (
	"fmt"
	"net"
	"time"
)

type Session struct {
	id              int32
	name            string
	lastInteraction time.Time
	messages        chan *Message
}

func NewSession(id int32, name string) *Session {
	return &Session{
		id:              id,
		name:            name,
		lastInteraction: time.Now(),
		messages:        make(chan *Message, 10),
	}
}

func (session *Session) Add(m *Message) {
	session.messages <- m
}

func (session *Session) Send(conn net.Conn) {
	select {
	case m := <-session.messages:
		m.Send(conn)
	default:
		MessageSend(conn, session.id, MR_BROKER, MT_NODATA, "")
	}
}

func (session *Session) stillActive() bool {
	if session.inActivity() > 1000000 {
		return false
	} else {
		return true
	}
}

func (session *Session) inActivity() int {
	now := time.Now()
	intMilliseconds := now.Sub(session.lastInteraction).Milliseconds()
	fmt.Printf("Client %v inActivity: %v\n", session.id, intMilliseconds)
	return int(intMilliseconds)
}
