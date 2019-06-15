#!/usr/bin/env python
import smach
import rospy
from std_msgs.msg import Empty
import threading
from butia_speech.srv import *

class WaitKeywordState(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['succeeded', 'error'])
        self.subscriber = rospy.Subscriber('butia/wakeup', Empty, self.callback)
        self.event = threading.Event()

    def execute(self, userdata):
        rospy.loginfo('executing state WAIT_KEYWORD')
        self.event.clear()
        self.event.wait()
        if self.event.is_set():
            rospy.loginfo('received keyword')
            return 'succeeded'
        return 'error'

    def callback(self, data):
        print("received keyword")
        self.event.set()


class SaySomethingState(smach.State):
    def __init__(self, text):
        smach.State.__init__(self, outcomes=['succeeded', 'error'])
        self.text = text

    def execute(self, userdata):
        rospy.wait_for_service('butia/synthesize_speech')
        synthesize_speech = rospy.ServiceProxy('butia/synthesize_speech', SynthesizeSpeech)
        resp = synthesize_speech(self.text, 'pt-br')
        if resp:
            return 'succeeded'
        return 'error'


if __name__ == '__main__':
    rospy.init_node('presentation_1')
    sm = smach.StateMachine(outcomes=['succeeded', 'error'])
    with sm:
        smach.StateMachine.add(
            'WAIT_KEYWORD1',
            WaitKeywordState(),
            transitions={
                'succeeded': 'INTRODUCE',
                'error': 'error'
            }
        )
        smach.StateMachine.add(
            'INTRODUCE',
            SaySomethingState('Oi, eu sou a Doris! Em que posso ajudar?'),
            transitions={
                'succeeded': 'WAIT_KEYWORD2',
                'error': 'error'
            }
        )
        smach.StateMachine.add(
            'WAIT_KEYWORD2',
            WaitKeywordState(),
            transitions={
                'succeeded': 'EXPLAIN',
                'error': 'error'
            }
        )
        smach.StateMachine.add(
            'EXPLAIN',
            SaySomethingState('Eu sou um ajudante para as tarefas de casa! Ainda estou em fase de programassaum e testes, por isso podemos apenas conversar!'),
            transitions={
                'succeeded': 'WAIT_KEYWORD3',
                'error': 'error'
            }
        )
        smach.StateMachine.add(
            'WAIT_KEYWORD3',
            WaitKeywordState(),
            transitions={
                'succeeded': 'TOAST',
                'error': 'error'
            }
        )
        smach.StateMachine.add(
            'TOAST',
            SaySomethingState('Vamos fazer um brinde! Tim Tim!'),
            transitions={
                'succeeded': 'succeeded',
                'error': 'error'
            }
        )
    outcome = sm.execute()

