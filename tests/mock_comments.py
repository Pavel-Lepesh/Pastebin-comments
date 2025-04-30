mock_comments = """[
  {
    "id": "661eb8d5b4a2f431dcb8f1d1",
    "note_hash_link": "hash_1",
    "user_id": 1,
    "created": "2025-04-28T12:00:00Z",
    "updated": "2025-04-28T12:00:00Z",
    "timezone": "Europe/Minsk",
    "body": "First test comment",
    "parent_id": null,
    "children": ["661eb8d5b4a2f431dcb8f1d3"]
  },
  {
    "id": "661eb8d5b4a2f431dcb8f1d2",
    "note_hash_link": "hash_3",
    "user_id": 2,
    "created": "2025-04-28T12:05:00Z",
    "updated": "2025-04-28T12:05:00Z",
    "timezone": "Europe/Minsk",
    "body": "Second test comment",
    "parent_id": null,
    "children": []
  },
  {
    "id": "661eb8d5b4a2f431dcb8f1d3",
    "note_hash_link": "hash_1",
    "user_id": 3,
    "created": "2025-04-28T12:10:00Z",
    "updated": "2025-04-28T12:10:00Z",
    "timezone": "Europe/Minsk",
    "body": "Reply to first comment",
    "parent_id": "661eb8d5b4a2f431dcb8f1d1",
    "children": []
  },
  {
    "id": "661eb8d5b4a2f431dcb8f1d4",
    "note_hash_link": "hash_3",
    "user_id": 4,
    "created": "2025-04-28T12:15:00Z",
    "updated": "2025-04-28T12:15:00Z",
    "timezone": "Europe/Minsk",
    "body": "Another root comment",
    "parent_id": null,
    "children": ["661eb8d5b4a2f431dcb8f1d5"]
  },
  {
    "id": "661eb8d5b4a2f431dcb8f1d5",
    "note_hash_link": "hash_3",
    "user_id": 5,
    "created": "2025-04-28T12:20:00Z",
    "updated": "2025-04-28T12:20:00Z",
    "timezone": "Europe/Minsk",
    "body": "Reply to another root comment",
    "parent_id": "661eb8d5b4a2f431dcb8f1d4",
    "children": []
  }
]"""