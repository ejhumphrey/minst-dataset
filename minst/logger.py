import logging


class ParamFilter(logging.Filter):
    def __init__(self, param=None):
        self.param = param

    def filter(self, record):
        if self.param is None:
            allow = True
        else:
            allow = self.param not in record.msg

        return allow


LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,  # this fixes the problem

    'filters': {
        'soxfilter': {
            '()': ParamFilter,
            'param': 'sox'
        }
    },

    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(filename)s %(funcName)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'filters': ['soxfilter']
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        }
    }
}


def get_config(level):
    theconfig = LOGGING_CONFIG.copy()
    theconfig['loggers']['']['level'] = level
    return theconfig
