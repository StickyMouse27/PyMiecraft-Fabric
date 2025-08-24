package top.fish1000.pymcfabric.executor;

import java.util.LinkedList;
import java.util.List;
import java.util.function.Consumer;
import java.util.function.IntSupplier;

import top.fish1000.pymcfabric.PymcMngr;

public class NamedAdvancedExecutor<T> extends NamedExecutor<T> {

    protected final List<NamedExecutorIdentifier<Consumer<T>>> callbackContinuousList;
    protected final List<NamedExecutorIdentifier<Consumer<T>>> callbackOnceList;

    public NamedAdvancedExecutor(IntSupplier tickSupplier) {
        super(tickSupplier);
        callbackContinuousList = new LinkedList<>();
        callbackOnceList = new LinkedList<>();
    }

    @Override
    public void tick(T data, String name) {
        // Utils.LOGGER.info("Looking for callback: tick{} @ {}", tickSupplier.get(),
        // name);
        super.tick(data, name);
        callbackContinuousList.forEach(callback -> {
            if (callback.name.equals(name)) {
                PymcMngr.LOGGER.info("Found callback(continuous) tick{} @ {}", tickSupplier.getAsInt(), name);
                callback.data.accept(data);
            }
        });
        callbackOnceList.forEach(callback -> {
            if (callback.name.equals(name)) {
                callback.data.accept(data);
                PymcMngr.LOGGER.info("Found callback(once), removed tick{} @ {}", tickSupplier.getAsInt(), name);
            }
        });
        callbackOnceList.removeIf(nv -> nv.name.equals(name));
    }

    public void tryTick(T data, String name) {
        try {
            tick(data, name);
        } catch (Exception e) {
            callbackContinuousList.clear();
            callbackOnceList.clear();
            callbackScheduled.clear();
            PymcMngr.LOGGER.error("Error in callback, skipped, callback list cleared: tick{} @ {}",
                    tickSupplier.getAsInt(), name);
            e.printStackTrace();
        }
    }

    public int pushScheduled(int tick, Consumer<T> callback, String name) {
        PymcMngr.LOGGER.info("Pushing callback(scheduled): tick{} @ {}", tickSupplier.getAsInt(), name);
        return super.push(tick, callback, name, TickType.RELATIVE);
    }

    public void removeScheduled(int id) {
        PymcMngr.LOGGER.info("Removing callback(scheduled): id: {}", id);
        super.remove(id);
    }

    public int pushOnce(Consumer<T> callback, String name) {
        PymcMngr.LOGGER.info("Pushing callback(once): tick{} @ {}", tickSupplier.getAsInt(), name);
        NamedExecutorIdentifier<Consumer<T>> id = new NamedExecutorIdentifier<>(callback, name);
        callbackOnceList.add(id);
        return id.id;
    }

    public void removeOnce(int id) {
        PymcMngr.LOGGER.info("Removing callback(once): {}", id);
        callbackOnceList.removeIf(identifier -> identifier.id == id);
    }

    public int pushContinuous(Consumer<T> callback, String name) {
        PymcMngr.LOGGER.info("Pushing callback(continuous): tick{} @ {}", tickSupplier.getAsInt(), name);
        NamedExecutorIdentifier<Consumer<T>> id = new NamedExecutorIdentifier<>(callback, name);
        callbackContinuousList.add(id);
        return id.id;
    }

    public void removeContinuous(int id) {
        PymcMngr.LOGGER.info("Removing callback(continuous): id{}", id);
        callbackContinuousList.removeIf(identifier -> identifier.id == id);
    }
}
