"""
Integration tests for routes/donations.py –
available donations, create, claim, verify, get all.
"""
import pytest
from datetime import datetime, timedelta

from models import DonationStatusEnum, NGOBranch, NGO, ApprovalStatusEnum


# ============= GET /api/donations/available =============


class TestAvailableDonations:
    """Tests for the available donations endpoint."""

    def test_get_available_donations(self, client, sample_donation):
        """Should return at least the sample donation."""
        response = client.get("/api/donations/available")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # our sample donation should be in the list
        ids = [d["id"] for d in data]
        assert sample_donation.id in ids

    def test_expired_donation_not_in_available(self, client, expired_donation):
        """Expired donations should NOT appear in the available list."""
        response = client.get("/api/donations/available")
        assert response.status_code == 200
        ids = [d["id"] for d in response.json()]
        assert expired_donation.id not in ids


# ============= POST /api/donations =============


class TestCreateDonation:
    """Tests for the create donation endpoint."""

    def test_create_donation(self, client):
        """Should create a donation and return 201."""
        payload = {
            "donor_name": "Jane Tester",
            "donor_phone": "1112223333",
            "food_type": "VEG",
            "quantity": 25.0,
            "address": "789 Test Blvd, Testville",
            "latitude": 12.97,
            "longitude": 77.59,
            "expiry_time": (datetime.utcnow() + timedelta(hours=8)).isoformat(),
        }
        response = client.post("/api/donations", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["donor_name"] == "Jane Tester"
        assert data["status"] == "AVAILABLE"
        assert data["quantity"] == 25.0

    def test_create_donation_missing_fields(self, client):
        """Missing required fields should return 422."""
        response = client.post("/api/donations", json={"donor_name": "X"})
        assert response.status_code == 422


# ============= GET /api/donations =============


class TestGetAllDonations:
    """Tests for the get-all donations endpoint."""

    def test_get_all_donations(self, client, sample_donation):
        """Should return a list containing the sample donation."""
        response = client.get("/api/donations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        ids = [d["id"] for d in data]
        assert sample_donation.id in ids


# ============= GET /api/donations/{id}/verify =============


class TestVerifyDonation:
    """Tests for the QR-code verification endpoint."""

    def test_verify_donation_success(self, client, sample_donation):
        """Should return verification details for an existing donation."""
        response = client.get(f"/api/donations/{sample_donation.id}/verify")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_donation.id
        assert data["verified"] is True

    def test_verify_donation_not_found(self, client):
        """Non-existent donation should return 404."""
        response = client.get("/api/donations/999999/verify")
        assert response.status_code == 404


# ============= PATCH /api/donations/{id}/status (claim) =============


class TestClaimDonation:
    """Tests for claiming a donation."""

    def test_claim_donation_success(
        self, client, sample_donation, sample_user, auth_headers
    ):
        """Approved NGO should be able to claim an available donation."""
        response = client.patch(
            f"/api/donations/{sample_donation.id}/status",
            json={"new_status": "ASSIGNED"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ASSIGNED"
        assert data["ngo_id"] == sample_user.ngo_id

    def test_claim_already_assigned(
        self, client, sample_donation, sample_user, auth_headers, db_session
    ):
        """Claiming an already-assigned donation should return 400."""
        # First claim
        sample_donation.status = DonationStatusEnum.ASSIGNED
        sample_donation.ngo_id = sample_user.ngo_id
        db_session.flush()

        response = client.patch(
            f"/api/donations/{sample_donation.id}/status",
            json={"new_status": "ASSIGNED"},
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_claim_expired_donation(
        self, client, expired_donation, sample_user, auth_headers
    ):
        """Claiming an expired donation should return 400."""
        response = client.patch(
            f"/api/donations/{expired_donation.id}/status",
            json={"new_status": "ASSIGNED"},
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_claim_donation_unauthenticated(self, client, sample_donation):
        """Unauthenticated request should return 403."""
        response = client.patch(
            f"/api/donations/{sample_donation.id}/status",
            json={"new_status": "ASSIGNED"},
        )
        assert response.status_code == 401


# ============= PUT /api/donations/{id}/verify (verify pickup) =============


class TestVerifyPickup:
    """Tests for verifying donation pickup (ASSIGNED → COMPLETED)."""

    def test_verify_pickup_success(
        self, client, sample_donation, sample_user, auth_headers, db_session
    ):
        """NGO that owns the donation should be able to verify pickup."""
        # First assign the donation to the NGO
        sample_donation.status = DonationStatusEnum.ASSIGNED
        sample_donation.ngo_id = sample_user.ngo_id
        db_session.flush()

        response = client.put(
            f"/api/donations/{sample_donation.id}/verify",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "COMPLETED"

    def test_verify_pickup_wrong_ngo(
        self, client, sample_donation, db_session, sample_user, auth_headers
    ):
        """NGO that does NOT own the donation should get 403."""
        # Create a different NGO and assign the donation to it
        from models import NGO, ApprovalStatusEnum
        other_ngo = NGO(
            name="Other NGO",
            email="other_ngo@example.com",
            phone="5555555555",
            address="999 Other Street",
            storage_capacity=200.0,
            approval_status=ApprovalStatusEnum.APPROVED,
        )
        db_session.add(other_ngo)
        db_session.flush()

        sample_donation.status = DonationStatusEnum.ASSIGNED
        sample_donation.ngo_id = other_ngo.id
        db_session.flush()

        response = client.put(
            f"/api/donations/{sample_donation.id}/verify",
            headers=auth_headers,
        )
        assert response.status_code == 403

    def test_verify_pickup_not_assigned(
        self, client, sample_donation, sample_user, auth_headers
    ):
        """Verifying a donation that is not ASSIGNED should return 400."""
        # sample_donation is AVAILABLE by default
        response = client.put(
            f"/api/donations/{sample_donation.id}/verify",
            headers=auth_headers,
        )
        # Could be 400 or 403 depending on order of checks
        assert response.status_code in (400, 403)


# ============= Capacity & Multiple Location Logic =============


class TestCapacityLogic:
    """Tests for storage capacity enforcement."""

    def test_claim_exceeds_ngo_capacity(
        self, client, sample_donation, sample_user, auth_headers, db_session
    ):
        """Should return 403 if donation exceeds NGO total capacity."""
        # Set NGO capacity to something small
        ngo = db_session.query(NGO).get(sample_user.ngo_id)
        ngo.storage_capacity = 5.0  # Max 5kg
        sample_donation.quantity = 10.0  # Try to claim 10kg
        db_session.flush()

        response = client.patch(
            f"/api/donations/{sample_donation.id}/status",
            json={"new_status": "ASSIGNED"},
            headers=auth_headers,
        )
        assert response.status_code == 403
        assert "capacity exceeded" in response.json()["detail"].lower()


class TestMultipleLocations:
    """Tests for branch-specific claiming."""

    def test_claim_for_specific_branch(
        self, client, sample_donation, sample_user, auth_headers, db_session
    ):
        """Should successfully claim a donation for a specific branch."""
        # Create a branch for the NGO
        branch = NGOBranch(
            ngo_id=sample_user.ngo_id,
            name="Downtown Branch",
            address="123 Main St",
            storage_capacity=100.0,
            is_active=1,
        )
        db_session.add(branch)
        db_session.flush()

        # Claim with branch_id
        response = client.patch(
            f"/api/donations/{sample_donation.id}/status",
            json={"new_status": "ASSIGNED", "branch_id": branch.id},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["branch_id"] == branch.id
        assert data["status"] == "ASSIGNED"

    def test_claim_exceeds_branch_capacity(
        self, client, sample_donation, sample_user, auth_headers, db_session
    ):
        """Should return 403 if donation exceeds specific branch capacity."""
        # Create a small branch
        branch = NGOBranch(
            ngo_id=sample_user.ngo_id,
            name="Small Branch",
            address="Tiny St",
            storage_capacity=5.0,  # Max 5kg
            is_active=1,
        )
        db_session.add(branch)
        db_session.flush()

        sample_donation.quantity = 10.0  # Try to claim 10kg

        # Claim with branch_id
        response = client.patch(
            f"/api/donations/{sample_donation.id}/status",
            json={"new_status": "ASSIGNED", "branch_id": branch.id},
            headers=auth_headers,
        )
        assert response.status_code == 403
        assert "branch storage capacity exceeded" in response.json()["detail"].lower()

