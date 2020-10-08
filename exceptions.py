class DataciteError(Exception):
    pass

class DataciteCompressedReportUUIDMissingError(DataciteError):
    pass

class DataciteAPIAuthenticationError(DataciteError):
    pass
