# Tool Reference

This reference is generated from `pkg/server/server.go` and covers all 16 Slack tools that the preserved runtime can expose through the FastMCP Python wrapper.

Availability notes:
- The repo-level `.env.example` enables an 8-tool read-focused subset by default.
- Set `SLACK_MCP_ENABLED_TOOLS=all` or an explicitly blank value to expose the full 16-tool surface.
- Some write-capable tools also respect additional runtime gate vars such as `SLACK_MCP_ADD_MESSAGE_TOOL`, `SLACK_MCP_REACTION_TOOL`, `SLACK_MCP_ATTACHMENT_TOOL`, and `SLACK_MCP_MARK_TOOL`.

## Conversations

### `conversations_history`

Get messages from the channel (or DM) by channel_id, the last row/column in the response is used as 'cursor' parameter for pagination if not empty

- Parameters:
  - `channel_id` | `string` | required | - `channel_id` (string): ID of the channel in format Cxxxxxxxxxx or its name starting with #... or @... aka #general or @username_dm.
  - `cursor` | `string` | optional | Cursor for pagination. Use the value of the last row and column in the response as next_cursor field returned from the previous request.
  - `limit` | `string` | optional default `1d` | Limit of messages to fetch in format of maximum ranges of time (e.g. 1d - 1 day, 1w - 1 week, 30d - 30 days, 90d - 90 days which is a default limit for free tier history) or number of messages (e.g. 50). Must be empty when 'cursor' is provided.
  - `include_activity_messages` | `boolean` | optional | If true, the response will include activity messages such as 'channel_join' or 'channel_leave'. Default is boolean false.

### `conversations_replies`

Get a thread of messages posted to a conversation by channelID and thread_ts, the last row/column in the response is used as 'cursor' parameter for pagination if not empty

- Parameters:
  - `channel_id` | `string` | required | ID of the channel in format Cxxxxxxxxxx or its name starting with #... or @... aka #general or @username_dm.
  - `thread_ts` | `string` | required | Unique identifier of either a thread's parent message or a message in the thread. ts must be the timestamp in format 1234567890.123456 of an existing message with 0 or more replies.
  - `cursor` | `string` | optional | Cursor for pagination. Use the value of the last row and column in the response as next_cursor field returned from the previous request.
  - `limit` | `string` | optional default `1d` | Limit of messages to fetch in format of maximum ranges of time (e.g. 1d - 1 day, 30d - 30 days, 90d - 90 days which is a default limit for free tier history) or number of messages (e.g. 50). Must be empty when 'cursor' is provided.
  - `include_activity_messages` | `boolean` | optional | If true, the response will include activity messages such as 'channel_join' or 'channel_leave'. Default is boolean false.

### `conversations_search_messages`

Search messages in a public channel, private channel, or direct message (DM, or IM) conversation using filters. All filters are optional, if not provided then search_query is required.

- Parameters:
  - `search_query` | `string` | optional | Search query to filter messages. Example: 'marketing report' or full URL of Slack message e.g. 'https://slack.com/archives/C1234567890/p1234567890123456', then the tool will return a single message matching given URL, herewith all other parameters will be ignored.
  - `filter_in_channel` | `string` | optional | Filter messages in a specific public/private channel by its ID or name. Example: 'C1234567890', 'G1234567890', or '#general'. If not provided, all channels will be searched.
  - `filter_in_im_or_mpim` | `string` | optional | Filter messages in a direct message (DM) or multi-person direct message (MPIM) conversation by its ID or name. Example: 'D1234567890' or '@username_dm'. If not provided, all DMs and MPIMs will be searched.
  - `filter_users_with` | `string` | optional | Filter messages with a specific user by their ID or display name in threads and DMs. Example: 'U1234567890' or '@username'. If not provided, all threads and DMs will be searched.
  - `filter_users_from` | `string` | optional | Filter messages from a specific user by their ID or display name. Example: 'U1234567890' or '@username'. If not provided, all users will be searched.
  - `filter_date_before` | `string` | optional | Filter messages sent before a specific date in format 'YYYY-MM-DD'. Example: '2023-10-01', 'July', 'Yesterday' or 'Today'. If not provided, all dates will be searched.
  - `filter_date_after` | `string` | optional | Filter messages sent after a specific date in format 'YYYY-MM-DD'. Example: '2023-10-01', 'July', 'Yesterday' or 'Today'. If not provided, all dates will be searched.
  - `filter_date_on` | `string` | optional | Filter messages sent on a specific date in format 'YYYY-MM-DD'. Example: '2023-10-01', 'July', 'Yesterday' or 'Today'. If not provided, all dates will be searched.
  - `filter_date_during` | `string` | optional | Filter messages sent during a specific period in format 'YYYY-MM-DD'. Example: 'July', 'Yesterday' or 'Today'. If not provided, all dates will be searched.
  - `cursor` | `string` | optional default `` | Cursor for pagination. Use the value of the last row and column in the response as next_cursor field returned from the previous request.
  - `filter_threads_only` | `boolean` | optional | If true, the response will include only messages from threads. Default is boolean false.
  - `limit` | `number` | optional default `20` | The maximum number of items to return. Must be an integer between 1 and 100.

### `conversations_unreads`

Get unread messages across all channels. With browser session tokens (xoxc/xoxd), uses a single API call for complete results. With OAuth user tokens (xoxp), scans a subset of channels per type (limited by max_channels) — results may be partial on large workspaces. Results are prioritized: DMs > group DMs > partner channels > internal channels.

- Parameters:
  - `channel_types` | `string` | optional default `all` | Filter by channel type: 'all' (default), 'dm' (direct messages), 'group_dm' (group DMs), 'partner' (ext-* channels), 'internal' (other channels).
  - `include_messages` | `boolean` | optional | If true (default), returns the actual unread messages. If false, returns only a summary of channels with unreads.
  - `mentions_only` | `boolean` | optional | If true, only returns channels where you have @mentions. Default is false.
  - `include_muted` | `boolean` | optional | If true, includes muted channels in results. Default is false (muted channels are excluded, matching Slack app behavior).
  - `max_channels` | `number` | optional default `50` | Maximum number of channels to fetch unreads from. Default is 50.
  - `max_messages_per_channel` | `number` | optional default `10` | Maximum messages to fetch per channel. Default is 10.

### `conversations_mark`

Mark a channel or DM as read. If no timestamp is provided, marks all messages as read.

- Parameters:
  - `channel_id` | `string` | required | ID of the channel in format Cxxxxxxxxxx or its name starting with #... or @... (e.g., #general, @username).
  - `ts` | `string` | optional | Timestamp of the message to mark as read up to. If not provided, marks all messages as read.

### `conversations_add_message`

Add a message to a public channel, private channel, or direct message (DM, or IM) conversation by channel_id and thread_ts.

- Parameters:
  - `channel_id` | `string` | required | ID of the channel in format Cxxxxxxxxxx or its name starting with #... or @... aka #general or @username_dm.
  - `thread_ts` | `string` | optional | Unique identifier of either a thread's parent message or a message in the thread_ts must be the timestamp in format 1234567890.123456 of an existing message with 0 or more replies. Optional, if not provided the message will be added to the channel itself, otherwise it will be added to the thread.
  - `text` | `string` | optional | Message text in specified content_type format. Example: 'Hello, world!' for text/plain or '# Hello, world!' for text/markdown.
  - `content_type` | `string` | optional default `text/markdown` | Content type of the message. Default is 'text/markdown'. Allowed values: 'text/markdown', 'text/plain'.

## Reactions And Attachments

### `reactions_add`

Add an emoji reaction to a message in a public channel, private channel, or direct message (DM, or IM) conversation.

- Parameters:
  - `channel_id` | `string` | required | ID of the channel in format Cxxxxxxxxxx or its name starting with #... or @... aka #general or @username_dm.
  - `timestamp` | `string` | required | Timestamp of the message to add reaction to, in format 1234567890.123456.
  - `emoji` | `string` | required | The name of the emoji to add as a reaction (without colons). Example: 'thumbsup', 'heart', 'rocket'.

### `reactions_remove`

Remove an emoji reaction from a message in a public channel, private channel, or direct message (DM, or IM) conversation.

- Parameters:
  - `channel_id` | `string` | required | ID of the channel in format Cxxxxxxxxxx or its name starting with #... or @... aka #general or @username_dm.
  - `timestamp` | `string` | required | Timestamp of the message to remove reaction from, in format 1234567890.123456.
  - `emoji` | `string` | required | The name of the emoji to remove as a reaction (without colons). Example: 'thumbsup', 'heart', 'rocket'.

### `attachment_get_data`

Download an attachment's content by file ID. Returns file metadata and content (text files as-is, binary files as base64). Maximum file size is 5MB.

- Parameters:
  - `file_id` | `string` | required | The ID of the attachment to download, in format Fxxxxxxxxxx. Attachment IDs can be found in message metadata when HasMedia is true or AttachmentCount > 0.

## Channels And Users

### `channels_list`

Get list of channels

- Parameters:
  - `channel_types` | `string` | required | Comma-separated channel types. Allowed values: 'mpim', 'im', 'public_channel', 'private_channel'. Example: 'public_channel,private_channel,im'
  - `sort` | `string` | optional | Type of sorting. Allowed values: 'popularity' - sort by number of members/participants in each channel.
  - `cursor` | `string` | optional | Cursor for pagination. Use the value of the last row and column in the response as next_cursor field returned from the previous request.
  - `limit` | `number` | optional default `100` | The maximum number of items to return. Must be an integer between 1 and 1000 (maximum 999).

### `users_search`

Search for users by name, email, or display name. Returns user details and DM channel ID if available.

- Parameters:
  - `query` | `string` | required | Search query - matches against real name, display name, username, or email.
  - `limit` | `number` | optional default `10` | Maximum number of results to return (1-100). Default is 10.

## User Groups

### `usergroups_list`

List all user groups (subteams) in the Slack workspace. User groups are mention groups like @engineering or @design that notify all members. Use this to discover available groups, check group membership counts, or find a group's ID before joining/updating it. Returns CSV with columns: id, name, handle, description, user_count, is_external.

- Parameters:
  - `include_users` | `boolean` | optional | Include list of user IDs in each group. Default is false.
  - `include_count` | `boolean` | optional | Include user count for each group. Default is true.
  - `include_disabled` | `boolean` | optional | Include disabled/archived groups. Default is false.

### `usergroups_me`

Manage your own user group membership. Use action='list' to see which groups you belong to. Use action='join' with a usergroup_id to add yourself to a group (e.g., to receive @mentions). Use action='leave' with a usergroup_id to remove yourself. This is the easiest way to join/leave groups without needing to know the full member list.

- Parameters:
  - `action` | `string` | required | Action to perform: 'list' returns CSV of groups you're a member of, 'join' adds you to a group, 'leave' removes you from a group.
  - `usergroup_id` | `string` | optional | ID of the user group (starts with 'S', e.g., 'S0123456789'). Required for 'join' and 'leave' actions. Get IDs from usergroups_list.

### `usergroups_create`

Create a new user group (mention group) in the Slack workspace. After creation, use usergroups_users_update to add members, or users can join themselves with usergroups_me. The handle becomes the @mention (e.g., handle='engineering' creates @engineering).

- Parameters:
  - `name` | `string` | required | Display name of the user group (e.g., 'Engineering Team', 'Design Squad').
  - `handle` | `string` | optional | The @mention handle without the @ symbol (e.g., 'engineering' for @engineering). Keep it short and lowercase. If omitted, Slack auto-generates one from the name.
  - `description` | `string` | optional | Purpose or description shown in group details (e.g., 'Backend and frontend engineers').
  - `channels` | `string` | optional | Comma-separated channel IDs where this group is commonly mentioned. Members get suggestions to join these channels.

### `usergroups_update`

Update a user group's metadata: name, handle (@mention), description, or default channels. Does NOT change members - use usergroups_users_update for that. At least one field must be provided.

- Parameters:
  - `usergroup_id` | `string` | required | ID of the user group to update (starts with 'S', e.g., 'S0123456789'). Get IDs from usergroups_list.
  - `name` | `string` | optional | New display name for the group.
  - `handle` | `string` | optional | New @mention handle (without @). Changing this changes how users mention the group.
  - `description` | `string` | optional | New description for the group.
  - `channels` | `string` | optional | New default channel IDs (comma-separated). Replaces existing default channels.

### `usergroups_users_update`

Replace all members of a user group with a new list. WARNING: This completely replaces the member list - any user not in the 'users' parameter will be removed. To add/remove just yourself, use usergroups_me instead. To add a single user without removing others, first get current members from usergroups_list with include_users=true, then call this with the combined list.

- Parameters:
  - `usergroup_id` | `string` | required | ID of the user group (starts with 'S', e.g., 'S0123456789'). Get IDs from usergroups_list.
  - `users` | `string` | required | Comma-separated user IDs that will become the COMPLETE member list (e.g., 'U0123456789,U9876543210'). All current members not in this list will be removed.

## Resources

- `slack://<workspace>/channels` returns a CSV channel directory resource.
- `slack://<workspace>/users` returns a CSV user directory resource.
