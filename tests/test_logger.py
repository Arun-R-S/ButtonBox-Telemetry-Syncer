import builtins
from buttonbox_syncer import logger


def test_logger_respects_levels(capsys):
    cfg = {"LoggingLevels": {"INFO": True, "WARN": True, "ERROR": True, "DEBUG": True, "DEBUGWARN": True, "DEBUGDEEP": True}}
    logger.configure(cfg)
    logger.info('info-msg')
    logger.debug('debug-msg')
    logger.warn('warn-msg')
    logger.error('error-msg')
    logger.debugWarn('debug-warn-msg')
    logger.debugDeep('debug-deep-msg')

    captured = capsys.readouterr()
    out = captured.out
    assert 'info-msg' in out
    assert 'debug-msg' in out
    assert 'warn-msg' in out
    assert 'error-msg' in out
    assert 'debug-warn-msg' not in out
    assert 'debug-deep-msg' not in out

def test_logger_suppresses_levels(capsys):
    cfg = {"LoggingLevels": {"INFO": False, "WARN": False, "ERROR": True, "DEBUG": False, "DEBUGWARN": False, "DEBUGDEEP": False}}
    logger.configure(cfg)
    logger.info('info-msg')
    logger.debug('debug-msg')
    logger.warn('warn-msg')
    logger.error('error-msg')
    logger.debugWarn('debug-warn-msg')
    logger.debugDeep('debug-deep-msg')

    captured = capsys.readouterr()
    out = captured.out
    assert 'info-msg' not in out
    assert 'debug-msg' not in out
    assert 'warn-msg' not in out
    assert 'error-msg' in out
    assert 'debug-warn-msg' not in out
    assert 'debug-deep-msg' not in out

def test_logger_error_includes_exception(capsys):
    cfg = {"LoggingLevels": {"INFO": True, "WARN": True, "ERROR": True, "DEBUG": True, "DEBUGWARN": True, "DEBUGDEEP": True}}
    logger.configure(cfg)
    try:
        1 / 0
    except ZeroDivisionError as e:
        logger.error('error-with-exc', exc=e)

    captured = capsys.readouterr()
    out = captured.out
    assert 'error-with-exc' in out
    assert 'Exception: division by zero' in out

def test_logger_default_config(capsys):
    # Reset to default config
    logger.configure(None)
    logger.info('info-msg')
    logger.warn('warn-msg')
    logger.error('error-msg')
    logger.debug('debug-msg')
    logger.debugWarn('debug-warn-msg')
    logger.debugDeep('debug-deep-msg')

    captured = capsys.readouterr()
    out = captured.out
    assert 'info-msg' in out
    assert 'warn-msg' in out
    assert 'error-msg' in out
    assert 'debug-msg' not in out
    assert 'debug-warn-msg' not in out
    assert 'debug-deep-msg' not in out