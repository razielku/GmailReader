"""Modify an existing Message's Labels.
"""

from apiclient import errors


def ModifyMessage(service, user_id, msg_id, msg_labels):
    """Modify the Labels on the given Message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The id of the message required.
    msg_labels: The change in labels.

  Returns:
    Modified message, containing updated labelIds, id and threadId.
  """
    try:
        message = service.users().messages().modify(userId=user_id, id=msg_id,
                                                    body=msg_labels).execute()

        label_ids = message['labelIds']

        # print ('Message ID: %s - With Label IDs %s' % (msg_id, label_ids))
        return message
    except errors.HttpError as error:
        print('An error occurred modifying: %s' % error)


def MarkReadLabel():
    return UpdateLabel('UNREAD', add=False)


def MarkUnreadLabel():
    return UpdateLabel('UNREAD')



def UpdateLabel(label, add=True):
    """Create object to update labels.

  Returns:
    A label update object.
  """
    if add:
        return {'removeLabelIds': [], 'addLabelIds': [label]}
    else:
        return {'removeLabelIds': [label], 'addLabelIds': []}
