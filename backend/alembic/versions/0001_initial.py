"""Initial PulseCrypt schema — encrypted columns only (no plaintext PII/EHR)."""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username_hash", sa.String(64), nullable=False, unique=True, index=True),
        sa.Column("username_enc", sa.LargeBinary(), nullable=False),
        sa.Column("email_enc", sa.LargeBinary(), nullable=False),
        sa.Column("phone_enc", sa.LargeBinary(), nullable=False),
        sa.Column("full_name_enc", sa.LargeBinary(), nullable=False),
        sa.Column("national_id_enc", sa.LargeBinary(), nullable=False),
        sa.Column("role_enc", sa.LargeBinary(), nullable=False),
        sa.Column("password_stored", sa.Text(), nullable=False),
        sa.Column("totp_secret_enc", sa.LargeBinary(), nullable=False),
        sa.Column("totp_confirmed", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("pii_mac", sa.LargeBinary(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "patient_profiles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column("address_enc", sa.LargeBinary(), nullable=False),
        sa.Column("blood_type_enc", sa.LargeBinary(), nullable=False),
        sa.Column("date_of_birth_enc", sa.LargeBinary(), nullable=False),
        sa.Column("emergency_contact_enc", sa.LargeBinary(), nullable=False),
        sa.Column("mac_tag", sa.LargeBinary(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "key_records",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("key_type", sa.String(16), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("public_key", sa.LargeBinary(), nullable=False),
        sa.Column("private_key_enc", sa.LargeBinary(), nullable=False),
        sa.Column("is_active", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("mac_tag", sa.LargeBinary(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "session_tokens",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True, index=True),
        sa.Column("stage", sa.String(16), nullable=False),
        sa.Column("blob_enc", sa.LargeBinary(), nullable=False),
        sa.Column("mac_tag", sa.LargeBinary(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "medical_records",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("payload_enc", sa.LargeBinary(), nullable=False),
        sa.Column("mac_tag", sa.LargeBinary(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "dh_exchanges",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("initiator_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("peer_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("params_json", sa.Text(), nullable=False),
        sa.Column("initiator_public", sa.Text(), nullable=False),
        sa.Column("peer_public", sa.Text(), nullable=True),
        sa.Column("initiator_private_enc", sa.LargeBinary(), nullable=False),
        sa.Column("peer_private_enc", sa.LargeBinary(), nullable=True),
        sa.Column("shared_secret_hash", sa.LargeBinary(), nullable=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("mac_tag", sa.LargeBinary(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "record_shares",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("record_id", sa.Integer(), sa.ForeignKey("medical_records.id"), nullable=False, index=True),
        sa.Column("from_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("to_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("dh_exchange_id", sa.Integer(), sa.ForeignKey("dh_exchanges.id"), nullable=False),
        sa.Column("payload_enc", sa.LargeBinary(), nullable=False),
        sa.Column("mac_tag", sa.LargeBinary(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("record_shares")
    op.drop_table("dh_exchanges")
    op.drop_table("medical_records")
    op.drop_table("session_tokens")
    op.drop_table("key_records")
    op.drop_table("patient_profiles")
    op.drop_table("users")
