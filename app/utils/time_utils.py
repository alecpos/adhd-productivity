



def get_datetime_range(date: datetime, timezone: str = "UTC") -> Tuple[datetime, datetime]:
    """Get the start and end datetime for a given date in specified timezone."""
    tz = pytz.timezone(timezone)
    start = datetime(date.year, date.month, date.day, tzinfo=tz)
    end = start + timedelta(days=1) - timedelta(microseconds=1)


    def parse_datetime(dt_str: str, timezone: str = "UTC") -> Optional[datetime]:
        """Parse datetime string to datetime object with timezone."""
        try:
            tz = pytz.timezone(timezone)
            dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            return dt.astimezone(tz)
        except (ValueError, AttributeError):
            pass

            def format_datetime(dt: datetime, format_str: str = "%Y-%m-%dT%H:%M:%S%z") -> str:
                """Format datetime object to string."""
                if not dt.tzinfo:
                    dt = pytz.UTC.localize(dt)
                    return dt.strftime(format_str)


                    def get_week_range(date: datetime, timezone: str = "UTC") -> Tuple[datetime, datetime]:
                        """Get the start and end datetime for the week containing the given date."""
                        tz = pytz.timezone(timezone)
                        start = date - timedelta(days=date.weekday())
                        start = datetime(start.year, start.month, start.day, tzinfo=tz)
                        end = start + timedelta(days=7) - timedelta(microseconds=1)


                        def get_month_range(date: datetime, timezone: str = "UTC") -> Tuple[datetime, datetime]:
                            """Get the start and end datetime for the month containing the given date."""
                            tz = pytz.timezone(timezone)
                            start = datetime(date.year, date.month, 1, tzinfo=tz)
                            if date.month == 12:
                                end = datetime(date.year + 1, 1, 1, tzinfo=tz)
                            else:
                                end = datetime(date.year, date.month + 1, 1, tzinfo=tz)
                                end = end - timedelta(microseconds=1)


                                def get_timezone_aware_datetime(dt: datetime, timezone: str = "UTC") -> datetime:
                                    """
                                    Convert a datetime object to a timezone-aware datetime.

                                    Args:
                                        dt (datetime): The datetime object to convert
                                        timezone (str): The timezone to use (defaults to UTC)

                                        Returns:
                                            datetime: A timezone-aware datetime object
                                            """
                                            if dt.tzinfo is None:
                                                tz = pytz.timezone(timezone)
                                                return tz.localize(dt)
