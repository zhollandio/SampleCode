class ProgramManagementReview(core_models.BaseModelWithHistory):
    fiscal_quarter = models.ForeignKey(
        core_models.FiscalQuarter, on_delete=models.PROTECT, related_name="+"
    )
    program = models.ForeignKey(
        Program, on_delete=models.PROTECT, related_name="program_management_review_set"
    )

    class Status(models.TextChoices):
        IN_PROGRESS = "P"
        SUBMITTED = "S"
        COMPLETED = "C"

    status = models.CharField(
        max_length=1, choices=Status.choices, default=Status.IN_PROGRESS
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("fiscal_quarter", "program"),
                name="unique_quarterly_program_review",
            ),
        )

    def __str__(self):
        return f"{self.program} - {self.fiscal_quarter}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        try:
            previous_fiscal_quarter = self.fiscal_quarter.get_previous_by_start_date()
        except core_models.FiscalQuarter.DoesNotExist:
            return

        previous_pmr = self.program.program_management_review_set.filter(
            fiscal_quarter=previous_fiscal_quarter
        ).first()

        if previous_pmr:
            # roll over (copy) open ActionItems from PMR from previous fiscal_quarter.
            for previous_action_item in previous_pmr.action_item_set.open():
                new_action_item = self.action_item_set.create(
                    description=previous_action_item.description,
                    date_opened=previous_action_item.date_opened,
                    date_due=previous_action_item.date_due,
                    assigned_to=previous_action_item.assigned_to,
                    status=previous_action_item.status,
                    priority=previous_action_item.priority,
                )
                previous_action_item.parent = new_action_item
                previous_action_item.save()

            # roll over (copy) open Risks from PMR from previous fiscal_quarter.
            for previous_risk in previous_pmr.risk_set.open():
                new_risk = self.risk_set.create(
                    identifier=previous_risk.identifier,
                    description=previous_risk.description,
                    date_opened=previous_risk.date_opened,
                    impact_date=previous_risk.impact_date,
                    likelihood=previous_risk.likelihood,
                    impact=previous_risk.impact,
                )
                previous_risk.parent = new_risk
                previous_risk.save()

    def get_absolute_url(self):
        return reverse(
            "Test:program-management-review-detail", kwargs={"uuid": self.uuid}
        )

    def get_submit_url(self):
        return reverse(
            "Test:program-management-review-submit", kwargs={"uuid": self.uuid}
        )

    def get_complete_url(self):
        return reverse(
            "Test:program-management-review-complete", kwargs={"uuid": self.uuid}
        )

    def get_history_url(self):
        return reverse(
            "Test:program-management-review-history", kwargs={"uuid": self.uuid}
        )

    def get_cost_detail_url(self):
        return reverse(
            "Test:program-management-review-cost-detail", kwargs={"uuid": self.uuid}
        )

    def get_cost_history_url(self):
        return reverse(
            "Test:program-management-review-cost-history", kwargs={"uuid": self.uuid}
        )

    def get_schedule_history_url(self):
        return reverse(
            "Test:program-management-review-schedule-history",
            kwargs={"uuid": self.uuid},
        )

    def get_performance_history_url(self):
        return reverse(
            "Test:program-management-review-performance-history",
            kwargs={"uuid": self.uuid},
        )

    def get_risk_history_url(self):
        return reverse(
            "Test:program-management-review-risk-history",
            kwargs={"uuid": self.uuid},
        )

    def get_schedule_detail_url(self):
        return reverse(
            "Test:program-management-review-schedule-detail",
            kwargs={"uuid": self.uuid},
        )

    def get_performance_detail_url(self):
        return reverse(
            "Test:program-management-review-performance-detail",
            kwargs={"uuid": self.uuid},
        )

    def get_risk_detail_url(self):
        return reverse(
            "Test:program-management-review-risk-detail", kwargs={"uuid": self.uuid}
        )

    def get_service_assessment_create_url(self):
        return reverse(
            "Test:service-assessment-create", kwargs={"pmr_uuid": self.uuid}
        )

    def get_capabilities_assessment_create_url(self):
        return reverse(
            "Test:capabilities-assessment-create", kwargs={"pmr_uuid": self.uuid}
        )

    def get_financial_assessment_create_url(self):
        return reverse(
            "Test:financial-assessment-create", kwargs={"pmr_uuid": self.uuid}
        )

    def get_architecture_compliance_assessment_create_url(self):
        return reverse(
            "Test:architecture-compliance-assessment-create",
            kwargs={"pmr_uuid": self.uuid},
        )

    def get_schedule_comment_create_url(self):
        return reverse("Test:schedule-comment-create", kwargs={"pmr_uuid": self.uuid})

    def get_schedule_item_create_url(self):
        return reverse("Test:schedule-item-create", kwargs={"pmr_uuid": self.uuid})

    def get_accomplishment_create_url(self):
        return reverse("Test:accomplishment-create", kwargs={"pmr_uuid": self.uuid})

    def get_progress_against_accomplishments_create_url(self):
        return reverse("Test:progress-create", kwargs={"pmr_uuid": self.uuid})

    def get_action_item_create_url(self):
        return reverse("Test:pmr-action-item-create", kwargs={"pmr_uuid": self.uuid})

    def get_risk_create_url(self):
        return reverse("Test:pmr-risk-create", kwargs={"pmr_uuid": self.uuid})

    def get_security_categorization_item_create_url(self):
        return reverse(
            "Test:security-categorization-item-create", kwargs={"pmr_uuid": self.uuid}
        )

    def get_notable_poam_item_create_url(self):
        return reverse("Test:notable-poam-item-create", kwargs={"pmr_uuid": self.uuid})

    def get_security_relevant_change_log_item_create_url(self):
        return reverse(
            "Test:security-relevant-change-log-item-create",
            kwargs={"pmr_uuid": self.uuid},
        )

    def get_continuous_monitoring_activity_item_create_url(self):
        return reverse(
            "Test:continuous-monitoring-activity-item-create",
            kwargs={"pmr_uuid": self.uuid},
        )

    def get_schedule_image_create_url(self):
        return reverse(
            "Test:schedule-image-create",
            kwargs={"pmr_uuid": self.uuid},
        )

    @cached_property
    def fiscal_year(self):
        return self.fiscal_quarter.fiscal_year

    @cached_property
    def previous_two_fiscal_years(self):
        previous_two_fiscal_years = [None, None]

        try:
            previous_two_fiscal_years[0] = self.fiscal_year.get_previous_by_start_date()
            previous_two_fiscal_years[
                1
            ] = (
                self.fiscal_year.get_previous_by_start_date().get_previous_by_start_date()
            )
        except core_models.FiscalYear.DoesNotExist:
            pass

        return previous_two_fiscal_years
