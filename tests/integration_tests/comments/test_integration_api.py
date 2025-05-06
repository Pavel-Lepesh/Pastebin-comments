import pytest


class TestIntegrationAPI:
    @pytest.mark.parametrize(
        "mock_hash_link, mock_page, mock_limit, expected_status",
        [
            ("hash_1", 1, 10, 200),
            ("unexpected_hash", 1, 10, 404),
            ("hash_1", 0, 10, 422),
            ("hash_1", 1, 101, 422),
        ],
    )
    async def test_get_all_notes_comments(
        self, mock_hash_link, mock_page, mock_limit, expected_status, async_client
    ):
        response = await async_client.get(
            f"/{mock_hash_link}/comments/",
            params={"page": mock_page, "limit": mock_limit},
        )
        assert response.status_code == expected_status

        if expected_status == 200:
            assert response.json()

    @pytest.mark.parametrize(
        "mock_comment_id, fetch_children, expected_status",
        [
            ("661eb8d5b4a2f431dcb8f1d1", False, 200),
            ("661eb8d5b4a2f431dcb8f1d1", True, 200),
            ("661eb8d5b4a2f431dcb8f100", True, 404),
            ("661eb8d5b4a2f431dcb8f100", False, 404),
            ("", True, 404),
            ("661eb8d5b4a2f431dcb8f100", None, 422),
        ],
    )
    async def test_get_comment_by_id(
        self, mock_comment_id, fetch_children, expected_status, async_client
    ):
        response = await async_client.get(
            f"/comments/{mock_comment_id}", params={"children": fetch_children}
        )

        assert response.status_code == expected_status

        if expected_status == 200:
            assert response.json()
            assert bool(response.json()["children"]) == fetch_children

    @pytest.mark.parametrize(
        "mock_hash_link, test_body, test_parent_id, expected_status",
        [
            ("hash_1", "content", None, 201),
            ("hash_1", "content", "661eb8d5b4a2f431dcb8f1d1", 201),
            ("hash_3", "content", "661eb8d5b4a2f431dcb8f1d1", 409),
            ("hash_1", "content", "661eb8d5b4a2f431dcb8f100", 404),
            ("hash_1", "", "661eb8d5b4a2f431dcb8f1d1", 422),
            ("hash_1", None, "661eb8d5b4a2f431dcb8f1d1", 422),
        ],
    )
    async def test_create_comment(
        self, mock_hash_link, test_body, test_parent_id, expected_status, async_client
    ):
        comment_data = {"body": test_body, "parent_id": test_parent_id}

        response = await async_client.post(
            f"/{mock_hash_link}/comments/", json=comment_data
        )

        assert response.status_code == expected_status

        if expected_status == 201:
            new_comment = response.json()
            assert new_comment["body"] == test_body
            assert new_comment["note_hash_link"] == mock_hash_link

    @pytest.mark.parametrize(
        "test_comment_id, test_body, expected_status",
        [
            ("661eb8d5b4a2f431dcb8f1d1", "new body", 204),
            ("661eb8d5b4a2f431dcb8f1d1", "", 422),
            ("661eb8d5b4a2f431dcb8f100", "new body", 404),
        ],
    )
    async def test_update_comment(
        self, test_comment_id, test_body, expected_status, async_client
    ):
        comment_data = {"body": test_body}
        response = await async_client.patch(
            f"/comments/{test_comment_id}", json=comment_data
        )

        assert response.status_code == expected_status

        if expected_status == 204:
            checking_response = await async_client.get(f"/comments/{test_comment_id}")

            assert checking_response.status_code == 200
            assert checking_response.json()["body"] == test_body

    @pytest.mark.parametrize(
        "test_comment_id, expected_status",
        [("661eb8d5b4a2f431dcb8f1d1", 204), ("661eb8d5b4a2f431dcb8f100", 404)],
    )
    async def test_delete_comment(self, test_comment_id, expected_status, async_client):
        response = await async_client.delete(f"/comments/{test_comment_id}")

        assert response.status_code == expected_status

        if expected_status == 204:
            checking_response = await async_client.get(f"/comments/{test_comment_id}")

            assert checking_response.status_code == 404
